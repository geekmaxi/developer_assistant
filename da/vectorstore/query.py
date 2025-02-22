import os
from da.vectorstore import DAVectorStore

if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv(os.path.join(os.environ.get("PYTHONPATH"), ".env"))

    vs = DAVectorStore()
    client = vs.vectorstore_client
    if not(client.is_connected()):
        client.connect()
    try:
        print(client.collections.get(vs.index_name).query)
        print(client.collections.get(vs.index_name).query.bm25(query="枚举"))
        print(client.collections.get(vs.index_name).query.)

        print(client.collections.get(vs.index_name).aggregate.over_all(total_count=True))
    finally:
        client.close()