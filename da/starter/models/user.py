from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from da.starter.models.base import BaseModel

class UserModel(BaseModel):
    __tablename__ = "user" # 表名
    # __bind__ = engine

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True) # 用户ID，主键，索引
    username = Column(String, index=True, default="") # 用户名，唯一，索引
    email = Column(String, index=True, default="") # 邮箱, 索引
    hashed_password = Column(String, default="") # 哈希密码