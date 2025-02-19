

from enum import Enum, unique

@unique
class ModelNamed(Enum):
    GPT_35 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4o = "gpt-4o"
    TEXT_EMBEDDING_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_ADA = "text-embedding-ada-002"


    DEEPSEEK_V3 = "deepseek-v3"
    DEEPSEEK_R1 = "deepseek-r1"
    LLAMA2_CHINESE = "llama2-chinese"
    LLAMA3 = "llama3.3-70b-instruct"
    # LLAMA3_CHINESE_8B = "llamafamily/llama3-chinese-8b-instruct"

    QWEN_MAX = "qwen-max-latest"

    # embeddings
    BGE_M3 = "bge-m3" # multilingual
    BGE_RERANKER_V2 = "BAAI/bge-reranker-v2-m3"

class Usage(Enum):
    CHAT = "chat",
    EMBEDDING = "embedding",
    GENERATION = "generation",
