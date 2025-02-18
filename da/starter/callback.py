from langchain_core.callbacks import BaseCallbackHandler

class MyCustomHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("LLM 开始运行")
    
    def on_llm_end(self, response, **kwargs):
        print("LLM 结束运行")
    
    def on_llm_new_token(self, token, **kwargs):
        print(f"新 Token: {token}")

    def on_retriever_start(self, serialized, query, *, run_id, parent_run_id = None, tags = None, metadata = None, **kwargs):
        return super().on_retriever_start(serialized, query, run_id=run_id, parent_run_id=parent_run_id, tags=tags, metadata=metadata, **kwargs)