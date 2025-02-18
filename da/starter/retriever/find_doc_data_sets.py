from typing import Sequence
from pydantic import BaseModel, Field
from langchain_core.documents import Document

class FindDocDataSets(BaseModel):
    docs: Sequence[Document] = Field(default=[])
    improved_question: str = Field(default="")
    viewpoint_questions: Sequence[str] = Field(default=[])