import os

from .exception import LLMException
from .interface import LLMInterface
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.language_models.base import BaseLanguageModel
from .constant import ModelNamed, Usage


class Openai(LLMInterface):
    @staticmethod
    def select(model_name: ModelNamed = ModelNamed.GPT_35, usage: Usage = Usage.CHAT) -> BaseLanguageModel:
        assert model_name in [ModelNamed.GPT_35, ModelNamed.GPT_4, ModelNamed.GPT_4_TURBO, ModelNamed.GPT_4o, ModelNamed.TEXT_EMBEDDING_ADA, ModelNamed.TEXT_EMBEDDING_LARGE, ModelNamed.TEXT_EMBEDDING_SMALL], f"Unsupported model: {model_name}"
        assert usage in [Usage.CHAT, Usage.EMBEDDING, Usage.GENERATION], f"Unsupported model usage: {usage}"
        # assert model_name in [ModelNamed.DEEPSEEK_V3, ModelNamed.DEEPSEEK_R1], f"Unsupported model: {model_name}"
        # assert usage in [Usage.CHAT, Usage.GENERATION], f"Unsupported model usage: {usage}"
        if usage == Usage.CHAT:
            return ChatOpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=8000,
            )
        elif usage == Usage.GENERATION:
            return OpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=8000,
            )
        elif usage == Usage.EMBEDDING:
            return OpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY"),
                model=model_name.value,
                temperature=0, # 设置成0最稳定；structured generation中稳定最重要
                max_tokens=2000,
            )
        else:
            raise LLMException(f"Unsupported model usage: {usage}")