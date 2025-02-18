
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from .interface import SplitterInterface
from .base import SplitterBase

class MarkdownSplitter(SplitterInterface, SplitterBase):
    def __init__(self, max_chunk_size: int = 1000, allow_chunk_overlap: int = 0):
        super().__init__(max_chunk_size=max_chunk_size, allow_chunk_overlap=allow_chunk_overlap)

    @property
    def splitter(self):
        return RecursiveCharacterTextSplitter(
            separators=[

                
                # Markdown特定分隔符
                "```\n",       # 代码块
                "# ",        # 一级标题
                "## ",       # 二级标题
                "### ",      # 三级标题
                "#### ",     # 四级标题

                "\n\n",      # 段落分隔
                "\n",        # 换行

                "</table>\n",

                # 其他可能的分隔符
                # "- ",        # 列表项
                # "> ",        #
                # 多种正则分隔模式
                # r'\n#{1,6}\s',     # Markdown标题
                # r'\n```[\s\S]*?```\n',    # 代码块
                # r'\n\*\* [\s\S]*? \*\*\n',    # 加粗
                # r'\n{2,}',         # 多个换行
                # r"(?i)<table>[\s\S]*?</table>" # 表格
                # r'\n\|.*\|\n',            # 表格行
                # r'\n>{1,}\s',             # 引用块
                # r'\n[-*+]\s',             # 列表项
                # r'(?<=\n)\s*\n',     # 带空白的换行
                # r'[。！？]',          # 中文标点
                # r'[.!?]',            # 英文标点
                # r'\s{2,}',           # 多个空白
                # r'(?<=\d)\s*(?=\w)', # 数字和单词之间
            ],
            chunk_size=self.max_chunk_size,
            chunk_overlap=self.allow_chunk_overlap,
            # keep_separator=True,
            keep_separator="start",
            is_separator_regex=True
        )

    def invoke(self, document) -> List[Document]:
        return self.splitter.split_documents(document)
    
    @staticmethod
    def split(document) -> List[Document]:
        splitter = MarkdownSplitter()
        return splitter.invoke(document)