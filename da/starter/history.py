import os
from langchain.memory import SQLChatMessageHistory
from da.llm import Ollama, ModelNamed, Usage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory

def get_message_history(session_id):
    return SQLChatMessageHistory(session_id=session_id, connection=os.getenv("MESSAGE_DB_URL"))

llm = Ollama.select(ModelNamed.LLAMA2_CHINESE, Usage.CHAT)

# 创建基础链
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

chain = prompt | llm

history = SQLChatMessageHistory(session_id="", connection=os.getenv("MESSAGE_DB_URL"))
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_message_history,
    input_messages_key="question",
    history_messages_key="history",
).with_config(run_name="ChatWithMessageHistory")

response = chain_with_history.invoke({"question": "你好"}, config={"configurable": {"session_id": "0c2ef7b0-5bae-481e-8fa3-5b61649a5aa2"}})

print(response)