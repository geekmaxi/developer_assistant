
import re
from typing import List
from urllib.parse import urljoin, urlparse
from langchain_community.document_loaders import RecursiveUrlLoader
from da.logger import logger
from da.document.splitter import MarkdownSplitter
from da.vectorstore.vectorstore import DAVectorStore
from .config import Config
from langchain.utils.html import PREFIXES_TO_IGNORE_REGEX, SUFFIXES_TO_IGNORE_REGEX
from da.document import FastapiDocumentParser, FastapiDocumentMeta, PythonDocumentParser, PythonDocumentMetadata, W3schoolDocumentParser, W3schoolDocumentMetadata
from langchain_core.documents import Document

class BaseIngester():
    _content_extractor = ""
    _metedata_extractor = ""
    _da_vectorstore: DAVectorStore = None
    _config: Config = {}

    def __init__(self, config: Config):
        self._config = config
        self._da_vectorstore = DAVectorStore()

    def url_filter(self, url):
        if self._config.only_current_dir and not (url.starswith(self._config.base_ur)):
            return False
        elif len(self._config.exclude):
            path = urlparse(url).path
            if any(_exclude in path for _exclude in self._config.exclude):
                return False
        # Drop trailing / to avoid duplicate pages.
        elif re.search(f"href=[\"']{PREFIXES_TO_IGNORE_REGEX}((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)", url)\
                or re.search(r"(?:[\#'\"]|\/[\#'\"])", url):
            return False
        return True

    @property
    def link_regex(self):
        regexes = [
            # 过滤js/image等文件,以及mailto/#/javascript等开头的
            f"href=[\"']{PREFIXES_TO_IGNORE_REGEX}(?![{'|'.join(self._config.exclude)}]{1}?)((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)",
            # 过滤#开头的
            # r"(?:[\#'\"]|\/[\#'\"])",
        ]
        # if self._config.only_current_dir:
        #     regexes.append(rf"{self._config.base_url}")

        # if len(self._config.exclude):
        #     regexes.append(rf"(?:[{'|'.join(self._config.exclude)}]{1})")

        logger.info(regexes)
        return regexes

    @property
    def splitter(self):
        return MarkdownSplitter()
    
    @property
    def loader(self):
        return RecursiveUrlLoader(
            url=self._config.base_url,
            timeout=10,
            max_depth=5,
            check_response_status=True,
            # Drop trailing / to avoid duplicate pages.
            link_regex=(
                rf"href=[\"']{PREFIXES_TO_IGNORE_REGEX}" # 排除 mailto/#/javascript等开头的
                # rf"((?!.*({EXCLUDE_REGEX})).*?)" # 排除自定义
                rf"((?:{SUFFIXES_TO_IGNORE_REGEX}.)*?)" # 排除以文件后缀结尾的，比如：js,png,epub等
                r"(?:[\#'\"]|\/[\#'\"])"
            ),
            # link_regex=self.link_regex,
            exclude_dirs=self._config.exclude,
            extractor=eval(self._content_extractor).extractor,
            metadata_extractor=eval(self._metedata_extractor).extractor,
            encoding="utf-8"
        )

    def invoke(self):
        EXCLUDE_REGEX="|".join([x.replace("-", "\-").replace("/", "\/") for x in self._config.exclude])
        EXCLUDE_REGEX= rf".*({EXCLUDE_REGEX}).*"

        documents = []
        counter = 0

        loader = self.loader

        for doc in loader.lazy_load():
            # logger.info(rf"^{self._config.base_url}")
            url_reg = self._config.base_url.replace('/', '\/').replace('-', '\-')
            if self._config.only_current_dir and not re.match(rf"^{url_reg}", doc.metadata["source"]):
                continue
            if len(self._config.exclude) and re.match(EXCLUDE_REGEX, doc.metadata['source']):
                continue

            """Links within the document are replaced with absolute paths"""
            for label, url in re.findall(r"\[([^\]]+)\]\(((?!http|mailto)[^)]+)\)", doc.page_content):
                doc.page_content = doc.page_content.replace(
                    f"[{label}]({url})", f"[{label}]({urljoin(doc.metadata['source'], url)})")
            documents.append(doc)

            counter += 1
            logger.info(f"loader counter:{counter}")

            # if counter >= 10:
            #     break
            if counter % 100 == 0:
                self._save_document(documents)
                documents = []
                # logger.info(f"loader counter:{counter}")

        if len(documents):
            self._save_document(documents)

        logger.info(
            f"Loaded {counter} documents from {self._config.base_url}")
        logger.info("-------------------------Load complete---------------------------------\n\n\n")

        # chunks = self.splitter.invoke(documents)

        # indexing_stats = self._da_vectorstore.append(chunks)
        # self._da_vectorstore.vectorstore_client.connect()
        # indexing_stats = index(
        #     chunks,
        #     record_manager=self._da_vectorstore.record_manager,
        #     vector_store=self._da_vectorstore.vectorstore,
        #     cleanup="incremental",
        #     source_id_key="source",
        #     force_update=(os.environ.get("FORCE_UPDATE") or "false").lower() == "true",
        # )

        # logger.info(f"Indexing stats: {indexing_stats}")
        # logger.info()
        # num_vecs = self._da_vectorstore.vectorstore_client.query.aggregate(self._da_vectorstore.index_name).with_meta_count().do()
        # logger.info(
        #     f"LangChain now has this many vectors: {num_vecs}",
        # )

    def _save_document(self, documents: List[Document]):
        chunks = self.splitter.invoke(documents)
        indexing_stats = self._da_vectorstore.append(chunks)
        logger.info(f"Indexing stats: {indexing_stats}")