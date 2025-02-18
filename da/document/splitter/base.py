class SplitterBase:
    max_chunk_size: int = 500,
    allow_chunk_overlap: int = 50

    def __init__(self, max_chunk_size: int = 500, allow_chunk_overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.allow_chunk_overlap = allow_chunk_overlap