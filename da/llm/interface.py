
from abc import ABC, abstractmethod
from langchain_core.language_models.base import BaseLanguageModel
from .constant import ModelNamed, Usage

class LLMInterface(ABC):
    @staticmethod
    def select(model_name: ModelNamed = "", usage: Usage = Usage.CHAT) -> BaseLanguageModel:
        pass