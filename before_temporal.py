import os

from haystack import Document, Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.document_stores.in_memory import InMemoryDocumentStore

os.environ["OPENAI_API_KEY"] = ""


def create_document_store():
    document_store = InMemoryDocumentStore()
    document_store.write_documents(
        [
            Document(content="My name is Jean and I live in Paris."),
            Document(content="My name is Mark and I live in Berlin."),
            Document(content="My name is Giorgio and I live in Rome."),
        ]
    )
    return document_store


def create_retriever(document_store):
    return InMemoryBM25Retriever(document_store=document_store)


def create_prompt_builder():
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


def create_llm():
    return OpenAIGenerator()


def create_rag_pipeline(retriever, prompt_builder, llm):
    rag_pipeline = Pipeline()
    rag_pipeline.add_component("retriever", retriever)
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("retriever", "prompt_builder.documents")
    rag_pipeline.connect("prompt_builder", "llm")
    return rag_pipeline


def run_query(rag_pipeline, question):
    results = rag_pipeline.run(
        {
            "retriever": {"query": question},
            "prompt_builder": {"question": question},
        }
    )
    return results["llm"]["replies"]


if __name__ == "__main__":
    document_store = create_document_store()
    retriever = create_retriever(document_store)
    prompt_builder = create_prompt_builder()
    llm = create_llm()
    rag_pipeline = create_rag_pipeline(retriever, prompt_builder, llm)

    question = "Who lives in Rome?"
    answer = run_query(rag_pipeline, question)
    print(answer)
