
GENERATION_QUESTION_TEMPLATE = """
任务说明：根据给定的问题输入，您需要输出3项信息（每项信息包含关键知识点、解决路径或是否需要示例等），并且每项信息不超过10个字。为了生成这些内容，请遵循以下步骤：

- 明确用户的真实需求。
- 确定所需的关键知识点。
- 判断是否需要提供示例来辅助理解。
- 分解问题的核心步骤。

注意事项：
- 本任务仅要求对问题进行分解，不需要直接解答问题。
- 新生成的内容必须与原始问题高度相关，避免偏离主题。
- 每项信息应当简洁明了，确保易于理解，且长度限制在10个字以内。
- 输出格式需为Markdown中的JSON数组格式。


示例：
问题：怎么在我个人电脑运行Ollama？
回答：
```json
[
    "如何在我的个人电脑上设置Ollama的本地模型？",
    "我的个人电脑需要满足哪些条件才能运行Ollama？",
    "安装和运行Ollama的过程中需要注意哪些步骤？"
]
```

问题：如何使用RecursiveUrlLoader从加载页面的内容？
回答：
```json
[
    "研究RecursiveUrlLoader文档", 
    "确定关键参数和使用方法", 
    "创建加载web内容的示例代码"
]
```

问题：{input}
回答：
```json
您的回答
```
"""

GENERATION_QUESTION_TEMPLATE_V2 = """
任务指令：根据给定的用户问题生成3个不同版本的问题或任务分解，目的是为了从矢量数据库中检索到更多相关文档。通过创建这些问题的不同表述方式，帮助用户克服基于距离的相似性搜索的一些限制。

核心要求：
- 每个版本必须准确反映原问题的核心意图。
- 尽可能覆盖不同的查询角度。
- 保持每个版本简洁明了，控制在10个字左右。
- 输出不必须以问题的形式呈现。

注意事项：
1. 确保所有生成的版本都与原始问题的主题紧密相关。
2. 可以考虑使用同义词替换、句式变换等方法来创造多样性。
3. 避免引入无关信息或改变问题的本质含义。


原问题：{question}
"""

# {format_instructions}

from pydantic import BaseModel, Field
class Questions(BaseModel):
    q1: str = Field(description="First generated question")
    q2: str = Field(description="Second generated question")
    q3: str = Field(description="Third generated question")

GENERATION_QUESTION_TEMPLATE_V3 = """
任务指令：根据给定的用户问题生成3个不同版本的问题，目的是为了从矢量数据库中检索到更多相关文档。通过创建这些问题的不同表述方式，帮助用户克服基于距离的相似性搜索的一些限制。

核心要求：
- 每个版本必须准确反映原问题的核心意图。
- 尽可能覆盖不同的查询角度。
- 保持每个版本简洁明了，控制在10个字左右。
- 输出不必须以问题的形式呈现。

注意事项：
1. 确保所有生成的版本都与原始问题的主题紧密相关。
2. 可以考虑使用同义词替换、句式变换等方法来创造多样性。
3. 避免引入无关信息或改变问题的本质含义。

{format_instructions}

原问题：{question}
"""

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
GENERATION_QUESTION_PROMPT = PromptTemplate(
    template=GENERATION_QUESTION_TEMPLATE_V3,
    input_variables=["question"],
    partial_variables={
        "format_instructions": PydanticOutputParser(
            pydantic_object=Questions
        ).get_format_instructions()
    }
)
def generation_question_chain(llm):
    return GENERATION_QUESTION_PROMPT | llm | PydanticOutputParser(
        pydantic_object=Questions
    )