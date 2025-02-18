from .base import BaseIngester
from da.document import W3schoolDocumentMetadata, W3schoolDocumentParser

class W3schoolIngester(BaseIngester):
    _content_extractor = W3schoolDocumentParser.__name__
    _metedata_extractor = W3schoolDocumentMetadata.__name__