# activities.py
import dataclasses
import json
from dataclasses import dataclass
from typing import Any, Optional, Type


from temporalio import activity
from temporalio.api.common.v1 import Payload
from temporalio.converter import (
    CompositePayloadConverter,
    DefaultPayloadConverter,
    EncodingPayloadConverter,
)

from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

class PipelinePayloadConverter(CompositePayloadConverter):
    def __init__(self) -> None:
        super().__init__(
            PipelineEncodingPayloadConverter(),
            *DefaultPayloadConverter.default_encoding_payload_converters,
        )


class PipelineEncodingPayloadConverter(EncodingPayloadConverter):
    def encode(self, value: Any) -> Optional[Payload]:
        if isinstance(value, Pipeline):
            return Payload(
                metadata={
                    "encoding": "json/haystack-pipeline",
                },
                data=json.dumps(value.to_config()).encode(),
            )
        return None

    def decode(self, payload: Payload, type_hint: Type[Any]) -> Any:
        if payload.metadata["encoding"] == "json/haystack-pipeline" and issubclass(
            type_hint, Pipeline
        ):
            config = json.loads(payload.data.decode())
            return Pipeline.from_config(config)
        return None


@dataclass
class QueryParams:
    question: str


@activity.defn
async def create_document_store() -> list:
    document_store = InMemoryDocumentStore()
    documents = [
        Document(content="My name is Jean and I live in Paris."),
        Document(content="My name is Mark and I live in Berlin."),
        Document(content="My name is Giorgio and I live in Rome."),
        Document(content="My name is Ana and I live in Lisbon."),
        Document(content="My name is Sofia and I live in Madrid."),
    ]
    document_store.write_documents(documents)
    return [doc.to_dict() for doc in documents]


@activity.defn
async def create_retriever(documents: list) -> InMemoryBM25Retriever:
    document_store = InMemoryDocumentStore()
    document_store.write_documents([Document.from_dict(doc) for doc in documents])
    return InMemoryBM25Retriever(document_store=document_store)


@activity.defn
async def create_prompt_builder() -> PromptBuilder:
    prompt_template = """
    Given these documents, answer the question.
    Documents:
    {% for doc in documents %}
        {{ doc.content }}
    {% endfor %}
    Question: {{question}}
    Answer:
    """
    return PromptBuilder(template=prompt_template)


@activity.defn
async def create_llm() -> OpenAIGenerator:
    return OpenAIGenerator()


@activity.defn
async def create_rag_pipeline(
    retriever: InMemoryBM25Retriever,
    prompt_builder: PromptBuilder,
    llm: OpenAIGenerator,
) -> Pipeline:
    rag_pipeline = Pipeline()
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("retriever", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm")
    return rag_pipeline


@activity.defn
async def run_query(rag_pipeline: Pipeline, params: QueryParams) -> str:
    results = rag_pipeline.run(
        {
            "retriever": {"query": params.question},
            "prompt_builder": {"question": params.question},
        }
    )
    return results["llm"]["replies"]
