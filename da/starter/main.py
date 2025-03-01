"""Main entrypoint for the app."""
import asyncio
import os
import dotenv
dotenv.load_dotenv(os.path.join(os.environ.get("PYTHONPATH"), ".env"))

from typing import Any, Dict, Optional, Union
from uuid import UUID

import langsmith
from da.starter.chain import ChatRequest, answer_chain
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from pydantic import BaseModel, Field
from da.starter.routes import register_routes
from da.starter.models import register_database
from da.logger import logger

from langsmith import Client
client = Client()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
register_database()


add_routes(
    app,
    answer_chain,
    path="/api",
    input_type=ChatRequest,
    config_keys=["metadata", "configurable", "tags"],
)

register_routes(
    app
)


class SendFeedbackBody(BaseModel):
    run_id: UUID
    key: str = "user_score"

    score: Union[float, int, bool, None] = None
    feedback_id: Optional[UUID] = None
    comment: Optional[str] = None


@app.post("/feedback")
async def send_feedback(body: SendFeedbackBody):
    client.create_feedback(
        body.run_id,
        body.key,
        score=body.score,
        comment=body.comment,
        feedback_id=body.feedback_id,
    )
    return {"result": "posted feedback successfully", "code": 200}

class UpdateFeedbackBody(BaseModel):
    feedback_id: UUID
    score: Union[float, int, bool, None] = None
    comment: Optional[str] = None


@app.patch("/feedback")
async def update_feedback(body: UpdateFeedbackBody):
    feedback_id = body.feedback_id
    if feedback_id is None:
        return {
            "result": "No feedback ID provided",
            "code": 400,
        }
    client.update_feedback(
        feedback_id,
        score=body.score,
        comment=body.comment,
    )
    return {"result": "patched feedback successfully", "code": 200}


# TODO: Update when async API is available
async def _arun(func, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args, **kwargs)


async def aget_trace_url(run_id: str) -> str:
    for i in range(5):
        try:
            await _arun(client.read_run, run_id)
            break
        except langsmith.utils.LangSmithError:
            await asyncio.sleep(1**i)

    if await _arun(client.run_is_shared, run_id):
        return await _arun(client.read_run_shared_link, run_id)
    return await _arun(client.share_run, run_id)


class GetTraceBody(BaseModel):
    run_id: UUID


@app.post("/get_trace")
async def get_trace(body: GetTraceBody):
    run_id = body.run_id
    if run_id is None:
        return {
            "result": "No LangSmith run ID provided",
            "code": 400,
        }
    return await aget_trace_url(str(run_id))

# # 请求模型
# class ThreadModel(BaseModel):
#     """线程更新模型"""
#     name: Optional[str] = Field(None, description="线程名称")
#     description: Optional[str] = Field(None, description="线程描述")
#     metadata: Optional[Dict[str, Any]] = Field(None, description="额外的元数据")
#     limit: Optional[int] = Field(None, description="限制数量")
#     offset: Optional[int] = Field(None, description="偏移量")
    
# @app.post("/api/threads", summary="Create a new thread.", tags=["Thread"])
# async def create_thread(body: ThreadModel):
#     thread = await graph_client.threads.create(
#         metadata=body.metadata
#     )
#     return {"result": {"thread_id": thread.thread_id}, "code": 200}

# @app.post("/api/threads/search", summary="List threads", tags=["Thread"])
# async def search_threads(body: ThreadModel, repsone: Response):
#     threads = await graph_client.threads.search(
#         metadata=body.metadata,
#         limit=body.limit,
#         offset=body.offset
#     )
#     return {"result": {"threads": threads}, "code": 200}

# @app.delete("/api/threads/{thread_id}", summary="Delete a thread.", tags=["Thread"])
# async def delete_thread(thread_id: str):
#     await graph_client.threads.delete(thread_id)

#     return {"result": "deleted thread successfully", "code": 200}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
