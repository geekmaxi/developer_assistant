from abc import ABC
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base

import os 
assert os.environ.get("USER_DB_URL") is not None

engine = create_engine(os.environ.get("USER_DB_URL"), echo=True) # 创建 SQLAlchemy 引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine) # 创建数据库会话工厂

# 实例化SessionLocal类
# db = SessionLocal()
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

Base = declarative_base() # 创建 SQLAlchemy 基类

    