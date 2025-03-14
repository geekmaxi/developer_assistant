REPHRASE_TEMPLATE = """
任务说明：根据提供的聊天记录，将后续问题改写为一个独立且完整的问题，确保新问题能够脱离上下文单独理解。

**任务要求：**

1. **分析背景信息**：仔细阅读并理解给定的后续问题。
2. **提取关键点**：从聊天记录中识别出与后续问题相关的所有重要信息。
3. **重构问题**：基于上述分析，将后续问题改写成一个独立、清晰简洁的新问题。


**注意事项：**

- 必须以后续问题为核心。
- 聊天记录是为了方便理解用户的意图，不应能作为独立问题的核心内容。


聊天记录：
{chat_history}
后续问题：{question}
独立问题：
"""