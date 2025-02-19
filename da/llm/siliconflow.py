"""
平台名称：硅基流动
官网地址：https://siliconflow.cn/zh-cn/
文档地址：https://docs.siliconflow.cn/cn/api-reference/
"""

import os
from langchain_core.language_models.base import BaseLanguageModel
from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.embeddings import LocalAIEmbeddings
from langchain_core.embeddings import Embeddings

from da.llm.constant import ModelNamed, Usage
from da.llm.exception import LLMException
from .interface import LLMInterface
from da.logger import logger
from urllib.parse import urljoin, urlparse

import requests
import typing

class SiliconFlowEmbeddings(Embeddings):
    def __init__(
        self, 
        model: str = "bge-large-zh-v1.5",
        api_key: str = "",
        base_url: str = os.getenv("SILICONFLOW_BASE_URL")
    ):
        self.api_key = api_key
        self.model = str(model)
        self.base_url = base_url

    def _embed(self, texts: typing.List[str]) -> typing.List[typing.List[float]]:
        assert self.base_url, "SiliconFlow base_url is required"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": texts
        }

        try:
            response = requests.post(urljoin(self.base_url, "embeddings"), headers=headers, json=payload)
            response.raise_for_status()
            embeddings = response.json()['data']
            return [embedding['embedding'] for embedding in embeddings]
        except Exception as e:
            logger.exception(e)
            print(f"Embedding 调用错误: {e}")
            return [[] for _ in texts]

    def embed_documents(self, texts: typing.List[str]) -> typing.List[typing.List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> typing.List[float]:
        return self._embed([text])[0]



class Siliconflow(LLMInterface):
    def select(model_name: ModelNamed = "", usage: Usage = Usage.CHAT) -> BaseLanguageModel:
        assert model_name in [ModelNamed.DEEPSEEK_V3, ModelNamed.DEEPSEEK_R1, ModelNamed.BGE_M3], f"Unsupported model: {model_name}"
        assert usage in [Usage.CHAT, Usage.EMBEDDING], f"Unsupported model usage: {type}"

        if model_name == ModelNamed.DEEPSEEK_R1:
            model_name = "deepseek-ai/DeepSeek-R1"
        elif model_name == ModelNamed.DEEPSEEK_V3:
            model_name = "deepseek-ai/DeepSeek-V3"
        elif model_name == ModelNamed.BGE_M3:
            model_name = "BAAI/bge-m3"

        if usage == Usage.EMBEDDING:
            return SiliconFlowEmbeddings(
                model = model_name,
                api_key=os.getenv("SILICONFLOW_API_KEY"),
                base_url=os.getenv("SILICONFLOW_BASE_URL")
            )
            return LocalAIEmbeddings(
                model=model_name,
                openai_api_base=os.getenv("SILICONFLOW_BASE_URL"),
                openai_api_key=os.getenv("SILICONFLOW_API_KEY"),
            )
        elif usage == Usage.CHAT:
            return ChatOpenAI(
                model_name=model_name,
                openai_api_base=os.getenv("SILICONFLOW_BASE_URL"),
                openai_api_key=os.getenv("SILICONFLOW_API_KEY"),
                temperature=0,
                max_tokens=8000
            )
        else:
            raise LLMException(f"Unsupported model usage: {usage}")
