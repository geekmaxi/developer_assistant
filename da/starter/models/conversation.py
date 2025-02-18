from datetime import datetime
from sqlalchemy import Column, DateTime, Integer
from .base import BaseModel
from sqlalchemy import String

class ConversationModel(BaseModel):
    __tablename__ = "conversation"
    # __bind__ = engine
    # __tablename__ = "users" # 表名
    # __bind__ = engine

    conversation_id = Column(Integer, primary_key=True, index=True, autoincrement=True) ## 主键，索引
    uuid = Column(String, unique=True, index=True) # uuid，索引
    user_id = Column(Integer, default=0) # 用户ID
    title = Column(String, index=True) # 标题，索引
    description = Column(String) # 说明

    # update_at = Column(DateTime, default=datetime(1, 1, 1, 0, 0, 0)) # 更新时间，默认值0001-01-01T00:00:00
    # created_at = Column(DateTime, default=datetime) # 创建时间，默认值为当前时间

    # def init_schema(self):
    #     self.metadata.create_all(bind=engine)
