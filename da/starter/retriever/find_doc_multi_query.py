from typing import Any, List, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
from langchain.retrievers.multi_query import MultiQueryRetriever, DEFAULT_QUERY_PROMPT, LineListOutputParser
from langchain_core.prompts import BasePromptTemplate

from da.logger import logger
from .find_doc_data_sets import FindDocDataSets


def ensure_subclass_method(func):
    def wrapper(self, *args, **kwargs):
        # 强制使用子类方法
        if type(self) is not FindDocMultiQueryRetriever:
            self.__class__ = FindDocMultiQueryRetriever
        return func(self, *args, **kwargs)
    return wrapper


class FindDocMultiQueryRetriever(MultiQueryRetriever):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generated_queries = []
    
    # @ensure_subclass_method
    def generate_queries(self, question: str, run_manager: CallbackManagerForRetrieverRun) -> List[str]:
        # 调用父类方法生成查询
        queries = super().generate_queries(question, run_manager)
        
        # 存储生成的查询
        self._generated_queries = queries
        return queries

    
    async def agenerate_queries(
        self, question: str, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[str]:
        # 调用父类方法生成查询
        queries = await super().agenerate_queries(question, run_manager)
        
        # 存储生成的查询
        self._generated_queries = queries
        return queries
    
    # @ensure_subclass_method
    def invoke(self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any) -> FindDocDataSets:
        """
        重写 invoke 方法，返回更丰富的结果
        """
        documents = super().invoke(input, config, **kwargs)
        logger.info( self._generated_queries)
        # return documents
        return FindDocDataSets(**{
            "docs": documents,
            "improved_question": input,
            "viewpoint_questions": self._generated_queries
        })

    async def ainvoke(
        self,
        input: str,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> FindDocDataSets:
        """
        重写 ainvoke 方法，返回更丰富的结果
        """
        documents = await super().ainvoke(input, config, **kwargs)
        return FindDocDataSets(**{
            "docs": documents,
            "improved_question": input,
            "viewpoint_questions": self._generated_queries
        })
    
    @classmethod
    def from_llm__(
        cls,
        retriever,
        llm,
        prompt: Optional[BasePromptTemplate] = None,
        include_original: bool = False,
    ) -> "FindDocMultiQueryRetriever":
        """
        类方法，用于创建实例
        """
        # 使用默认或自定义 prompt
        prompt = prompt or DEFAULT_QUERY_PROMPT
        
        # 创建 LLM 链
        output_parser = LineListOutputParser()
        llm_chain = prompt | llm | output_parser
        
        return cls(
            retriever=retriever,
            llm_chain=llm_chain,
            include_original=include_original
        )