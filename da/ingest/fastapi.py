from .base import BaseIngester
from da.document import FastapiDocumentMeta, FastapiDocumentParser

class FastapiIngester(BaseIngester):
    _content_extractor = FastapiDocumentParser.__name__
    _metedata_extractor = FastapiDocumentMeta.__name__