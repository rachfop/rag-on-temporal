# worker.py
import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from activities import (create_document_store, create_llm,
                        create_prompt_builder, create_rag_pipeline,
                        create_retriever, run_query, PipelineEncodingPayloadConverter)
from workflow import QueryWorkflow

interrupt_event = asyncio.Event()


async def main():
    client = await Client.connect(
        "localhost:7233",
        data_converter=PipelineEncodingPayloadConverter,
    )
    worker = Worker(
        client,
        task_queue="rag-task-queue",
        workflows=[QueryWorkflow],
        activities=[
            create_document_store,
            create_retriever,
            create_prompt_builder,
            create_llm,
            create_rag_pipeline,
            run_query,
        ],
    )

    print("\nWorker started, ctrl+c to exit\n")
    await worker.run()
    try:
        await interrupt_event.wait()
    finally:
        print("\nShutting down the worker\n")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nInterrupt received, shutting down...\n")
        interrupt_event.set()
        loop.run_until_complete(loop.shutdown_asyncgens())
