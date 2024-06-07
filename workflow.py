from datetime import timedelta
from typing import Dict

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import QueryParams, create_document_store, run_query


@workflow.defn
class QueryWorkflow:
    @workflow.run
    async def run(self, params: QueryParams) -> Dict[str, str]:
        documents = await workflow.execute_activity(
            create_document_store,
            start_to_close_timeout=timedelta(seconds=10),
        )

        answer = await workflow.execute_activity(
            run_query,
            (params.question, documents),
            start_to_close_timeout=timedelta(seconds=30),
        )

        return {"answer": answer}
