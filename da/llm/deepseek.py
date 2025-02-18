import os

from .exception import LLMException
from .interface import LLMInterface
from langchain_openai import ChatOpenAI, OpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models.base import BaseLanguageModel
from .constant import ModelNamed, Usage

class DeepSeek(LLMInterface):
    @staticmethod
    def select(model_name: ModelNamed = ModelNamed.DEEPSEEK_V3, usage: Usage = Usage.CHAT) -> BaseLanguageModel:
        assert model_name in [ModelNamed.DEEPSEEK_V3, ModelNamed.DEEPSEEK_R1], f"Unsupported model: {model_name}"
        assert usage in [Usage.CHAT, Usage.GENERATION], f"Unsupported model usage: {usage}"
        
        if usage == Usage.CHAT:
            return ChatDeepSeek(
                base_url=os.getenv("DEEPSEEK_BASE_URL"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=2000,
            )
        elif usage == Usage.GENERATION:
            return OpenAI(
                base_url=os.getenv("DEEPSEEK_BASE_URL_2"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=2000,
            )
        else:
            raise LLMException(f"Unsupported model usage: {usage}")