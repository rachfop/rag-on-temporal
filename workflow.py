# workflow.py
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import (
        QueryParams,
        create_document_store,
        create_llm,
        create_prompt_builder,
        create_rag_pipeline,
        create_retriever,
        run_query,
    )


@workflow.defn
class QueryWorkflow:
    @workflow.run
    async def run(self, params: QueryParams) -> dict:
        document_store = await workflow.execute_activity(
            create_document_store,
            start_to_close_timeout=timedelta(seconds=10),
        )

        retriever = await workflow.execute_activity(
            create_retriever,
            document_store,
            start_to_close_timeout=timedelta(seconds=10),
        )

        prompt_builder = await workflow.execute_activity(
            create_prompt_builder,
            start_to_close_timeout=timedelta(seconds=10),
        )

        llm = await workflow.execute_activity(
            create_llm,
            start_to_close_timeout=timedelta(seconds=10),
        )

        rag_pipeline = await workflow.execute_activity(
            create_rag_pipeline,
            retriever,
            prompt_builder,
            llm,
            start_to_close_timeout=timedelta(seconds=20),
        )

        answer = await workflow.execute_activity(
            run_query,
            rag_pipeline,
            params,
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {"answer": answer}
