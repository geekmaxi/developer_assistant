from da.starter.models.user import UserModel
from da.starter.models.conversation import ConversationModel

from .plugin import Base, engine, get_db


def register_database():
    Base.metadata.create_all(bind=engine)



__all__ = [
    "UserModel",
    "ConversationModel",
    "register_database",
    "get_db"
]