from .base import BaseIngester
from da.document import LangchainDocumentMetadata, LangchainDocumentParser
from langchain_community.document_loaders import SitemapLoader

class LangchainIngester(BaseIngester):
    _content_extractor = LangchainDocumentParser.__name__
    _metedata_extractor = LangchainDocumentMetadata.__name__

    @property
    def loader(self):
        return SitemapLoader(
            self._config.base_url,
            filter_urls=["https://python.langchain.com/"],
            parsing_function=eval(self._content_extractor).extractor,
            meta_function=eval(self._metedata_extractor).extractor,
            default_parser="lxml",
            requests_kwargs={
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
                    # "Authorization": "Bearer your_token_here",
                    # 可以添加其他自定义 headers
                }
            }
            # parsing_function=LangchainDocumentParser.extractor,
            # parsing_function=LangchainDocumentParser.extractor,
        )