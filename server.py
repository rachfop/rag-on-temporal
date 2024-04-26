# server.py
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Body, FastAPI, HTTPException
from temporalio.client import Client

from activities import PipelineEncodingPayloadConverter, QueryParams
from workflow import QueryWorkflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.temporal_client = await Client.connect(
        "localhost:7233", data_converter=PipelineEncodingPayloadConverter
    )
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/query")
async def query(question: str = Body(..., embed=True)):
    client = app.state.temporal_client
    try:
        result = await client.execute_workflow(
            QueryWorkflow.run,
            QueryParams(question),
            id=f"query-{question}",
            task_queue="rag-task-queue",
        )
        answer = result.get("answer", "Answer not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer": answer}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
