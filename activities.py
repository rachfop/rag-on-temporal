from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from temporalio import activity

from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore


@dataclass
class QueryParams:
    question: str


@activity.defn
async def create_document_store() -> List[Dict[str, Any]]:
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


async def create_retriever(documents: List[Dict[str, Any]]) -> InMemoryBM25Retriever:
    document_store = InMemoryDocumentStore()
    document_store.write_documents([Document.from_dict(doc) for doc in documents])
    return InMemoryBM25Retriever(document_store=document_store)


async def create_prompt_builder() -> str:
    prompt_template = """
    Given these documents, answer the question.
    Documents:
    {% for doc in documents %}
        {{ doc.content }}
    {% endfor %}
    Question: {{question}}
    Answer:
    """
    return prompt_template


async def create_llm() -> OpenAIGenerator:
    return OpenAIGenerator()


async def create_rag_pipeline(
    retriever: InMemoryBM25Retriever,
    prompt_template: str,
    llm: OpenAIGenerator,
) -> Pipeline:
    rag_pipeline = Pipeline()
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component(
        "prompt_builder", PromptBuilder(template=prompt_template)
    )
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("retriever", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm")
    return rag_pipeline


@activity.defn
async def run_query(params: Tuple[str, List[Dict[str, Any]]]) -> str:
    question, documents = params
    document_store = InMemoryDocumentStore()
    document_store.write_documents([Document.from_dict(doc) for doc in documents])
    retriever = InMemoryBM25Retriever(document_store=document_store)

    prompt_template = """
    Given these documents, answer the question.
    Documents:
    {% for doc in documents %}
        {{ doc.content }}
    {% endfor %}
    Question: {{question}}
    Answer:
    """
    prompt_builder = PromptBuilder(template=prompt_template)
    llm = OpenAIGenerator()

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("retriever", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm")

    results = rag_pipeline.run(
        {"retriever": {"query": question}, "prompt_builder": {"question": question}}
    )

    # Extract and return the first reply
    return (
        results["llm"]["replies"][0]
        if "llm" in results
        and "replies" in results["llm"]
        and results["llm"]["replies"]
        else "No answer found"
    )
