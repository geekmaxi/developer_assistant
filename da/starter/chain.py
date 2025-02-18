import os, requests
from operator import itemgetter
from typing import Dict, List, Optional, Sequence

# import weaviate
# from constants import WEAVIATE_DOCS_INDEX_NAME
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
# from ingest import get_embeddings_model
from langchain_anthropic import ChatAnthropic
# from langchain_community.chat_models import ChatCohere

from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_cohere import ChatCohere
# from langchain_community.vectorstores import Weaviate
from langchain_core.documents import Document
from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
# from langchain_core.pydantic_v1 import BaseModel
from pydantic import BaseModel
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import (
    ConfigurableField,
    Runnable,
    RunnableBranch,
    RunnableLambda,
    RunnablePassthrough,
    RunnableSequence,
    RunnableWithMessageHistory,
    chain
)
from langchain_fireworks import ChatFireworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from .history import create_message_history_chain, format_history

# from langsmith import Client
from da.logger import logger
from .prompt import RESPONSE_TEMPLATE

from .retriever.retriever import create_retriever_chain
from da.vectorstore import DAVectorStore
da_vectorstore = DAVectorStore()

from langchain.globals import set_debug

# 开启全局 verbose
set_debug(True)

# RESPONSE_TEMPLATE = """\
# You are an expert programmer and problem-solver, tasked with answering any question \
# about computer programming.

# Generate a comprehensive and informative answer of 80 words or less for the \
# given question based solely on the provided search results (URL and content). You must \
# only use information from the provided search results. Use an unbiased and \
# journalistic tone. Combine search results together into a coherent answer. Do not \
# repeat text. Cite search results using [${{number}}] notation. Only cite the most \
# relevant results that answer the question accurately. Place these citations at the end \
# of the sentence or paragraph that reference them - do not put them all at the end. If \
# different results refer to different entities within the same name, write separate \
# answers for each entity.

# You should use bullet points in your answer for readability. Put citations where they apply
# rather than putting them all at the end.

# If there is nothing in the context relevant to the question at hand, just say "Hmm, \
# I'm not sure." Don't try to make up an answer.

# Anything between the following `context`  html blocks is retrieved from a knowledge \
# bank, not part of the conversation with the user. 

# <context>
#     {context} 
# <context/>

# REMEMBER: If there is no relevant information within the context, just say "Hmm, I'm \
# not sure." Don't try to make up an answer. Anything between the preceding 'context' \
# html blocks is retrieved from a knowledge bank, not part of the conversation with the \
# user.You need to reply in Chinese unless the user specifies a language.\
# """

COHERE_RESPONSE_TEMPLATE = """\
You are an expert programmer and problem-solver, tasked with answering any question \
about Langchain.

Generate a comprehensive and informative answer of 80 words or less for the \
given question based solely on the provided search results (URL and content). You must \
only use information from the provided search results. Use an unbiased and \
journalistic tone. Combine search results together into a coherent answer. Do not \
repeat text. Cite search results using [${{number}}] notation. Only cite the most \
relevant results that answer the question accurately. Place these citations at the end \
of the sentence or paragraph that reference them - do not put them all at the end. If \
different results refer to different entities within the same name, write separate \
answers for each entity.

You should use bullet points in your answer for readability. Put citations where they apply
rather than putting them all at the end.

If there is nothing in the context relevant to the question at hand, just say "Hmm, \
I'm not sure." Don't try to make up an answer.

REMEMBER: If there is no relevant information within the context, just say "Hmm, I'm \
not sure." Don't try to make up an answer. Anything between the preceding 'context' \
html blocks is retrieved from a knowledge bank, not part of the conversation with the \
user.\
"""


# client = Client()

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["*"],
# )


# WEAVIATE_URL = os.environ["WEAVIATE_URL"]
# WEAVIATE_API_KEY = os.environ["WEAVIATE_API_KEY"]


class ChatRequest(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]]




def config_interceptor(input_data, config):
    # 拦截并处理配置
    metadata = config.get('metadata', {})
    
    # 根据元数据动态调整
    if metadata.get('debug_mode'):
        print("调试信息:", input_data)
    
    return input_data

def format_docs(docs: Sequence[Document]) -> str:
    formatted_docs = []
    for i, doc in enumerate(docs):
        doc_string = f"<doc id='{i+1}'>{doc.page_content}</doc>"
        formatted_docs.append(doc_string)
    return "\n".join(formatted_docs)


def serialize_history(request: ChatRequest, config, **kwargs):
    # logger.info(request)
    logger.info(kwargs)
    chat_history = request["chat_history"] or []
    converted_chat_history = []
    for message in chat_history:
        if message.get("human") is not None:
            converted_chat_history.append(HumanMessage(content=message["human"]))
        if message.get("ai") is not None:
            converted_chat_history.append(AIMessage(content=message["ai"]))
    return converted_chat_history

def get_session_history(config):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string="sqlite:///chat_history.db"
    )

def create_chain(llm: LanguageModelLike) -> Runnable:
    retriever_chain = create_retriever_chain(
        llm
    ).with_config(run_name="FindDocs")
    context = (
        RunnablePassthrough.assign(doc_sets = retriever_chain)
        .assign(context=lambda x: format_docs(x["doc_sets"].docs))
        .assign(improved_question=lambda x: x["doc_sets"].improved_question)
        .assign(viewpoint_questions=lambda x: "- " + "\n- ".join(x["doc_sets"].viewpoint_questions))
        .with_config(run_name="RetrieveDocs")
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RESPONSE_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{improved_question}"),
        ]
    )
    default_response_synthesizer = prompt | llm

    cohere_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", COHERE_RESPONSE_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{improved_question}"),
        ]
    )

    @chain
    def cohere_response_synthesizer(input: dict) -> RunnableSequence:
        return cohere_prompt | llm.bind(source_documents=input["docs"])

    response_synthesizer = (
        default_response_synthesizer.configurable_alternatives(
            ConfigurableField("llm"),
            default_key="deepseek_v3",
            # deepseek_v3=deepseek_v3,
            llama2_chinese=default_response_synthesizer,
            qwen_max=default_response_synthesizer,
            openai_gpt_3_5_turbo=default_response_synthesizer,
        )
        | StrOutputParser()
    ).with_config(run_name="GenerateResponse")
    
    llmchain = (
        RunnablePassthrough.assign(chat_history=format_history)
        | context
        | response_synthesizer
    )

    history_chain = create_message_history_chain(llmchain)

    return history_chain
    # RunnableWithMessageHistory(
    #     runnable=llmchain,
    #     get_session_history=lambda session_id: [],
    #     input_messages_key="question",
    #     history_messages_key="chat_history",
    # ).with_config(run_name="ChatWithMessageHistory") | RunnableLambda(
    #     lambda x: {"answer": x}
    # )

#   "deepseek_v3",
#   "llama2_chinese",
#   "openai_gpt_3_5_turbo",
#   "qwen_max"

from da.llm import Openai, DeepSeek, Ollama, Bailian, Usage, ModelNamed
gpt_3_5 = Openai.select(ModelNamed.GPT_35, Usage.GENERATION)
deepseek_v3 = Bailian.select(ModelNamed.DEEPSEEK_V3, Usage.CHAT)
llama2_chinese = Ollama.select(ModelNamed.LLAMA2_CHINESE, Usage.CHAT)
qwen_max = Bailian.select(ModelNamed.QWEN_MAX, Usage.CHAT)

# gpt_3_5 = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, streaming=True)
# claude_3_haiku = ChatAnthropic(
#     model="claude-3-haiku-20240307",
#     temperature=0,
#     max_tokens=4096,
#     anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "not_provided"),
# )
# fireworks_mixtral = ChatFireworks(
#     model="accounts/fireworks/models/mixtral-8x7b-instruct",
#     temperature=0,
#     max_tokens=16384,
#     fireworks_api_key=os.environ.get("FIREWORKS_API_KEY", "not_provided"),
# )
# gemini_pro = ChatGoogleGenerativeAI(
#     model="gemini-pro",
#     temperature=0,
#     max_tokens=16384,
#     convert_system_message_to_human=True,
#     google_api_key=os.environ.get("GOOGLE_API_KEY", "not_provided"),
# )
# cohere_command = ChatCohere(
#     model="command",
#     temperature=0,
#     cohere_api_key=os.environ.get("COHERE_API_KEY", "not_provided"),
# )
llm = deepseek_v3.configurable_alternatives(
    # This gives this field an id
    # When configuring the end runnable, we can then use this id to configure this field
    ConfigurableField(id="llm"),
    default_key="deepseek_v3",
    # deepseek_v3=deepseek_v3,
    llama2_chinese=llama2_chinese,
    qwen_max=qwen_max,
    openai_gpt_3_5_turbo=gpt_3_5,
).with_fallbacks(
    [deepseek_v3, gpt_3_5, qwen_max, llama2_chinese]
)

# retriever = get_retriever()
answer_chain = create_chain(llm)
