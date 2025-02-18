from abc import ABC, abstractmethod
from typing import Iterable, List, Union
from langchain_core.documents import Document

class SplitterInterface(ABC):
    @abstractmethod
    def invoke(self, document: Union[Iterable[Document], Document]):
        pass