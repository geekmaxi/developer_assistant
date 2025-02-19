"""
平台名称：阿里百练
官网地址：https://bailian.console.aliyun.com/
文档地址：https://help.aliyun.com/zh/model-studio/getting-started/what-is-model-studio
"""

import os

from .exception import LLMException
from .interface import LLMInterface
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.language_models.base import BaseLanguageModel
from .constant import ModelNamed, Usage

class Bailian(LLMInterface):
    @staticmethod
    def select(model_name: ModelNamed = ModelNamed.DEEPSEEK_V3, usage: Usage = Usage.CHAT) -> BaseLanguageModel:
        assert model_name in [ModelNamed.DEEPSEEK_V3, ModelNamed.DEEPSEEK_R1, ModelNamed.QWEN_MAX, ModelNamed.LLAMA3], f"Unsupported model: {model_name}"
        assert usage in [Usage.CHAT, Usage.GENERATION], f"Unsupported model usage: {usage}"
        if usage == Usage.CHAT:
            return ChatOpenAI(
                base_url=os.getenv("BAILIAN_BASE_URL"),
                api_key=os.getenv("BAILIAN_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=8000,
            )
        elif usage == Usage.GENERATION:
            return OpenAI(
                base_url=os.getenv("BAILIAN_BASE_URL"),
                api_key=os.getenv("BAILIAN_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=8000,
            )
        else:
            raise LLMException(f"Unsupported model usage: {usage}")