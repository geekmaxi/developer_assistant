
import time
from datetime import datetime
from typing import List, Union
from sqlalchemy import Column, DateTime, Float
from sqlalchemy.orm import Session
from .plugin import Base, engine, get_db

class BaseModel(Base):
    __abstract__ = True
    __fuzzy_fields__ = {}
    __reserved_fields__ = ["sort_mode", "sort_prop", "limit", "offset"]

    __session: Session = None
    def __init__(self, **kwargs):
        super().__init__()

        self.__session = list(get_db())[0]

        if kwargs:
            self.from_dict(kwargs)

    updated_ts = Column(Float, default=0, onupdate=time.time)
    updated_at = Column(DateTime, default=datetime(1970, 1, 1, 0, 0, 0), onupdate=datetime.now) # 更新时间，默认值0001-01-01T00:00:00
    created_ts = Column(Float, default=time.time)
    created_at = Column(DateTime, default=datetime.now) # 创建时间，默认值为当前时间

    def init_schema(self):
        self.metadata.create_all(bind=engine)

    def filter(self, **kwargs):
        items = []
        for key, value in kwargs.items():
            if key in self.__reserved_fields__:
                continue
            # if self.__fuzzy_fields__.get(key) is not None:
            #     items.append(getattr(type(self), self.__fuzzy_fields__[
            #                     key]).like('%{}%'.format(value)))
            elif type(value) == list:
                items.append(getattr(type(self), key).in_(value))
            elif type(value) == dict:
                if value.get('gt') is not None:
                    items.append(getattr(type(self), key)
                                    > value.get('gt'))
                elif value.get('gte') is not None:
                    items.append(getattr(type(self), key)
                                    >= value.get('gte'))
                elif value.get('lt') is not None:
                    items.append(getattr(type(self), key)
                                    < value.get('lt'))
                elif value.get('lte') is not None:
                    items.append(getattr(type(self), key)
                                    <= value.get('lte'))
                elif value.get('neq', ''):
                    items.append(getattr(type(self), key) != value.get('neq'))
                elif value.get('isnot') is not None:
                    items.append(getattr(type(self), key).isnot_(value.get('isnot')))
                elif value.get('notin') is not None:
                    items.append(getattr(type(self), key).notin_(value.get('notin')))
                else:
                    items.append(getattr(type(self), key) == value)
            else:
                items.append(getattr(type(self), key) == value)
        # logger.debug(items)
        return self.__session.query(type(self)).filter(*items)
    
    def search(self, **kwargs) -> Union[List[any], None]:
        _query = self.filter(**kwargs)
        if kwargs.get('sort_prop') is not None and kwargs.get('sort_mode') is not None:
            if kwargs.get('sort_mode') == 'asc':
                _query = _query.order_by(getattr(type(self), kwargs.get('sort_prop')).asc())
            elif kwargs.get('sort_mode') == 'desc':
                _query = _query.order_by(getattr(type(self), kwargs.get('sort_prop')).desc())

        if kwargs.get('limit') is not None:
            _query = _query.limit(kwargs.get('limit'))
        if kwargs.get('offset') is not None:
            _query = _query.offset(kwargs.get('offset'))

        result = _query.all()
        return result
    
    def count(self, **kwargs):
        _query = self.filter(**kwargs)
        return _query.count()
    
    def get_one(self, **kwargs):
        _query = self.filter(**kwargs)
        return _query.one() if _query.count() else (type(self))()
    
    def insert(self, data: Union[any, None] = None):
        if isinstance(data, list):
            self.__session.add_all(data)
        elif data:
            self.__session.add(data)
        else:
            self.__session.add(self)
        
        self.__session.commit()
        self.__session.flush()

    def to_dict(self, include: List[str] = None, exclude: List[str] = None):
        data = {}
        for key in self.__mapper__.c.keys():
            # 排除指定字段
            if exclude:
                try:
                    exclude.index(key)
                except ValueError:
                    if getattr(self, key, None) is not None:
                        data[key] = getattr(self, key)
                continue

            # 包含指定字段
            if include:
                try:
                    include.index(key)
                    if getattr(self, key, None) is not None:
                        data[key] = getattr(self, key)
                except ValueError:
                    pass
                continue

            if getattr(self, key, None) is not None:
                data[key] = getattr(self, key)
        return data

    # def to_dict(self, result: Union[List[any], any, None] = None, include: List[str] = None, exclude: List[str] = None) -> dict:
    #     if type(result) == list:
    #         return [v.__to_dict(include = include, exclude = exclude) for v in result]
    #     else:
    #         if result:
    #             return result.__to_dict(include = include, exclude = exclude)
    #         else:
    #             return self.__to_dict(include = include, exclude = exclude)

    def from_dict(self, dict):
        for key in self.__mapper__.c.keys():
            # logger.info(key, dict.get(key, None))
            if dict.get(key, None) is not None:
                # logger.info(key, dict.get(key))
                self.__dict__[key] = dict.get(key)

