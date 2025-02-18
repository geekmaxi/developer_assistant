
from da.vectorstore.vectorstore import DAVectorStore
from da.logger import logger

if __name__ == "__main__":
    vector_store = DAVectorStore()
    logger.info(vector_store.clean())
    logger.info(vector_store.vectorstore_client.collections.delete(vector_store.index_name))