
from typing import Annotated, Optional, Union
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from da.starter.models import get_db, ConversationModel
from da.starter.authorizer import get_token_data, TokenData

class CreateConversationBody(BaseModel):
    title: str
    description: Optional[str] = ""

class GetConversationBody(BaseModel):
    uuid: str

class SearchConversationBody(BaseModel):
    uuid: Optional[str]
    limit: Optional[int] = 10
    offset: Optional[int] = 0

def add_conversation_route(
    app: Union[FastAPI, APIRouter],
    namespace="/api/conversation"
):
    tags = ["Conversation"]

    @app.get(f"{namespace}/", summary="Get Conversation Information", tags=tags, include_in_schema = True)
    async def get_infomation(
        uuid: str = "",
        db: Session = Depends(get_db),
        tokenData: Annotated = Depends(get_token_data)
        ):
        query = {
            "uuid": uuid,
            "user_id": tokenData.user_id
        }
        model = ConversationModel()
        result = model.get_one(**query)
        return {
            "result": result.to_dict(include=["title", "description", "uuid", "created_ts", "updated_ts"]),
            "code": 200
        }

    @app.get(f"{namespace}/search", summary="Search Conversation", tags=tags, include_in_schema=True)
    async def search(uuid: str = "", limit: int = 10, offset: int = 0,
                     db: Session = Depends(get_db),
                     tokenData: Annotated = Depends(get_token_data)):

        query = {
            "user_id": tokenData.user_id,
            "limit": limit,
            "offset": offset
        }
        if uuid:
            query.uuid = uuid
        
        model = ConversationModel()
        cv_list = model.search(**query)
        # results = db.query(ConversationModel).filter(getattr(ConversationModel, "user_id") == tokenData.user_id).offset(offset).limit(limit)
        return {
            "result": [r.to_dict(include=["title", "description", "uuid", "created_ts", "updated_ts"]) for r in cv_list],
            "code": 200
        }
    
    @app.post(f"{namespace}/", summary="Create Conversation", tags=tags)
    async def create_conversation(
        body: CreateConversationBody,
        db: Session = Depends(get_db),
        tokenData: Annotated = Depends(get_token_data)
        ):

        conversation = ConversationModel(
            user_id = tokenData.user_id,
            uuid = str(uuid4()),
            title = body.title,
            description = body.description
        )
        conversation.insert()
        return {
            "result": {"uuid": conversation.uuid},
            "code": 200
        }
    