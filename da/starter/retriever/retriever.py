


from operator import itemgetter
from da.starter.prompt import REPHRASE_TEMPLATE, GENERATION_QUESTION_TEMPLATE_V2
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableLambda, Runnable
from langchain_core.language_models import LanguageModelLike

from da.vectorstore import DAVectorStore

from da.logger import logger
from .find_doc_multi_query import FindDocMultiQueryRetriever





def create_retriever_chain(
    llm: LanguageModelLike
) -> Runnable:
    da_vectorstore = DAVectorStore()
    # 向量数据库作为检索器
    retriever = da_vectorstore.vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={'k': 3, "score_threshold": .6}
    )

    # llm = Bailian.select(ModelNamed.DEEPSEEK_R1)

    # 依据历史记录重新生成新的问题，以保持问题的上下文关联
    condense_question_prompt = PromptTemplate.from_template(REPHRASE_TEMPLATE)
    condense_question_chain = (
        condense_question_prompt | llm | StrOutputParser()
    ).with_config(
        run_name="CondenseQuestion",
    )

    # prompt = PromptTemplate(
    #         input_variables=["question"],
    #         template=GENERATION_QUESTION_TEMPLATE_V2
    #     )
    # llm_chain = prompt | llm | LineListOutputParser()
    # multi_retriever = ExtendedMultiQueryRetriever(
    #     retriever=retriever,
    #     llm_chain=llm_chain,
    # )

    # # 多角度查询器
    multi_retriever = FindDocMultiQueryRetriever.from_llm__(
        retriever=retriever, llm=llm, prompt=PromptTemplate(
            input_variables=["question"],
            template=GENERATION_QUESTION_TEMPLATE_V2
        )
    )

    # 查询链
    chain = RunnableBranch(
        (
            # 如果有历史聊天记录，则用上下文和新问题进行问题压缩
            RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
                run_name="HasChatHistoryCheck"
            ),
            (condense_question_chain | multi_retriever).with_config(
                run_name="RetrievalChainWithHistory"),
        ),
        (
            RunnableLambda(itemgetter("question")).with_config(
                run_name="Itemgetter:question"
            )
            | multi_retriever
        ).with_config(run_name="RetrievalChainWithNoHistory"),
    ).with_config(run_name="RouteDependingOnChatHistory")

    return chain


