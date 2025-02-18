
from da.ingest.base import BaseIngester
from da.document import PythonDocumentParser, PythonDocumentMetadata
from da.logger import logger

class PythonIngester(BaseIngester):
    _content_extractor = PythonDocumentParser.__name__
    _metedata_extractor = PythonDocumentMetadata.__name__

    