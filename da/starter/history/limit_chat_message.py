from typing import List
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import BaseMessage
from sqlalchemy import Column, Integer, Text, delete, select


class LimitedSQLChatMessageHistory(SQLChatMessageHistory):
    def __init__(self, session_id, limited_messages: int = 5, **kwargs):
        kwargs["async_mode"] = kwargs.get("async_mode", True)
        super().__init__(session_id=session_id, **kwargs)
        self.limited_messages = limited_messages

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve all messages from db"""
        with self._make_sync_session() as session:
            result = (
                session.query(self.sql_model_class)
                .where(
                    getattr(self.sql_model_class, self.session_id_field_name)
                    == self.session_id
                )
                .order_by(self.sql_model_class.id.asc())
                .limit(self.limited_messages)
            )
            messages = []
            for record in result:
                messages.append(self.converter.from_sql_model(record))
            return messages
        
    async def aget_messages(self) -> List[BaseMessage]:
        """Retrieve all messages from db"""
        await self._acreate_table_if_not_exists()
        async with self._make_async_session() as session:
            stmt = (
                select(self.sql_model_class)
                .where(
                    getattr(self.sql_model_class, self.session_id_field_name)
                    == self.session_id
                )
                .order_by(self.sql_model_class.id.asc())
                .limit(self.limited_messages)
            )
            result = await session.execute(stmt)
            messages = []
            for record in result.scalars():
                messages.append(self.converter.from_sql_model(record))
            return messages