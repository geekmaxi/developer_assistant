import os
from .limit_chat_message import LimitedSQLChatMessageHistory
from langchain_core.runnables import Runnable, RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage


def get_message_history(session_id):
    return LimitedSQLChatMessageHistory(session_id=session_id, connection=os.getenv("MESSAGE_DB_URL"))

def create_message_history_chain(chain: Runnable):
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_message_history,
        input_messages_key="question",
        history_messages_key="history",
    ).with_config(run_name="ChatWithMessageHistory")

    return chain_with_history

def format_history(input):
    def _format(messages):
        for message in messages:
            if type(message) == HumanMessage:
                yield HumanMessage(content=message.content.strip())
            elif type(message) == AIMessage:
                yield AIMessage(content=message.content.strip())
            else:
                continue

    return list(_format(input["history"]))