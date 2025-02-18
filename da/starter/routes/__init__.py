from typing import Union

from fastapi import APIRouter, FastAPI
from .user import add_user_routes
from .conversation import add_conversation_route

def register_routes(app: Union[FastAPI, APIRouter]):
    add_user_routes(app)
    add_conversation_route(app)

__all__ = [
    "add_user_routes",
    "add_conversation_route",
    "register_routes"
]