
from typing import Union, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import JSONResponse
from http.cookies import SimpleCookie
from da.starter.authorizer import create_access_token, get_token_data, TokenData
from da.starter.models import UserModel, get_db
from da.logger import logger
from uuid import uuid4
from sqlalchemy.orm import Session

class UserRequestModel(BaseModel):
    user_id: Optional[str] = Field(0, description="User ID")
    email: Optional[str] = Field(None, description="User Email")
    name: Optional[str] = Field(None, description="User Name")
    password: Optional[str] = Field(None, description="User Password")


def add_user_routes(
    app: Union[FastAPI, APIRouter],
    namespace="/api/user"
):
    tags = ["User"]
    @app.post(
        f"{namespace}/login",
        summary="User Login",
        tags=tags
    )
    async def user_login(user: UserRequestModel, db: Session = Depends(get_db)):
        user_info = UserModel(
            username = f"guest-{str(uuid4())}"
        )
        user_info.insert()
        # user_id = db.add(user_info)
        # db.commit()
        token_data = TokenData(
            user_id = user_info.user_id,
            username = user_info.username,
        )
        token = create_access_token(token_data)
        response = JSONResponse(content={"result": {"token": token, }, "code": 200})
        response.set_cookie("token", token, httponly=True)
        return response
    