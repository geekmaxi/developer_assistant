import os
from langchain_core.language_models.base import BaseLanguageModel
from langchain_ollama import ChatOllama, OllamaLLM, OllamaEmbeddings
from da.llm.constant import ModelNamed, Usage
from .interface import LLMInterface


class Ollama(LLMInterface):
    @staticmethod
    def select(model_name: ModelNamed = "", usage: Usage = Usage.CHAT) -> BaseLanguageModel:
        assert model_name in [ModelNamed.LLAMA2_CHINESE, ModelNamed.BGE_M3], f"Unsupported model: {model_name}"
        assert usage in [Usage.CHAT, Usage.GENERATION, Usage.EMBEDDING], f"Unsupported model usage: {usage}"
        
        if usage == Usage.CHAT:
            return ChatOllama(
                model=model_name.value,
                base_url=os.getenv("OLLAMA_BASE_URL"),
                temperature=0, max_tokens=8000
            )
        elif usage == Usage.GENERATION:
            return OllamaLLM(
                model=model_name.value,
                base_url=os.getenv("OLLAMA_BASE_URL"),
                temperature=0, max_tokens=8000
            )
        elif usage == Usage.EMBEDDING:
            return OllamaEmbeddings(
                model=model_name.value,
                base_url=os.getenv("OLLAMA_BASE_URL"),
            )
        else:
            raise LLMException(f"Unsupported model usage: {usage}")

