import os
from typing import Iterable
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from langchain_weaviate import WeaviateVectorStore
from langchain.indexes import SQLRecordManager
from langchain.indexes import index, IndexingResult
from langchain_core.documents import Document
from da.llm import SiliconFlowEmbeddings, ModelNamed, Siliconflow, Usage, Ollama

from .weaviate_collection_config import weaviate_collection_config

import weaviate
from da.logger import logger

class DAVectorStore(object):
    _vectorstore_client: any = None
    _vectorstore_type: str = ""
    _vectorstore: VectorStore = None
    _embeddings: Embeddings = None
    _index_name: str = "Development_Assistant_Document"
    _record_manger: SQLRecordManager = None
    
    def __init__(self):
        """初始化向量数据库、向量模型"""

        """初始化Embeddings模型"""
        self._embeddings = Siliconflow.select(ModelNamed.BGE_M3, Usage.EMBEDDING)
        # self._embeddings = OllamaEmbeddings(
        #     # model="nomic-embed-text",
        #     model="bge-m3",
        #     base_url="http://127.0.0.1:11434",
        #     # model_kwargs={
        #     #     "device": "cpu"
        #     # },
        #     # encode_kwargs = {
        #     #     "normallize_embeddings": True,
        #     #     "query_instruction": ""
        #     # }
        # )
        # self._embeddings = Siliconflow.select(ModelNamed.BGE_M3, Usage.EMBEDDING)
        # self._embeddings = SiliconFlowEmbeddings(
        #     model=ModelNamed.BGE_M3,
        #     api_key=os.environ["SILICONFLOW_API_KEY"],
        #     base_url=os.environ["SILICONFLOW_BASE_URL"]
        # )

        """初始化向量数据库"""
        self._vectorstore_type = "weaviate"
        with weaviate.connect_to_local(skip_init_checks = False, host="127.0.0.1") as client:
            client.connect()
            logger.info(client.collections)
            if not client.collections.exists(self._index_name):
                client.collections.create_from_dict(weaviate_collection_config)
                # client.collections.create_from_config
            self._vectorstore_client = client
            self._vectorstore = WeaviateVectorStore(
                client=self._vectorstore_client,
                index_name=self._index_name,
                text_key="text",
                embedding=self._embeddings,
                attributes=["source", "title"]
            )

        """初始化SQLRecordManager"""
        self._record_manger = SQLRecordManager(
            f"{self._vectorstore_type}/{self._index_name}", db_url=os.environ["RECORD_MANAGER_DB_URL"]
        )
        self._record_manger.create_schema()

    def append(self, documents: Iterable[Document]) -> IndexingResult:
        # if not(self.vectorstore_client.is_connected()):
        #     self.vectorstore_client.connect()

        try:
            return index(
                documents,
                self.record_manager,
                self.vectorstore,
                cleanup="incremental",
                source_id_key="source"
            )
        finally:
            self._vectorstore_client.close()

    def clean(self) -> IndexingResult:
        # if not(self.vectorstore_client.is_connected()):
        #     self.vectorstore_client.connect()
        try:
            return index(
                [],
                self.record_manager,
                self.vectorstore,
                cleanup="full",
                source_id_key="source"
            )
        finally:
            self._vectorstore_client.close()

    @property
    def vectorstore(self) -> VectorStore:
        self.vectorstore_client
        return self._vectorstore
    
    @property
    def vectorstore_client(self) -> any:
        if not(self._vectorstore_client.is_connected()):
            self._vectorstore_client.connect()
        return self._vectorstore_client
    
    @property
    def record_manager(self) -> SQLRecordManager:
        return self._record_manger
    
    @property
    def index_name(self) -> str:
        return self._index_name
    
    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings
    
    @property
    def vectorstore_type(self) -> str:
        return self._vectorstore_type
    
    @classmethod
    def new(self):
        return DAVectorStore()
    
