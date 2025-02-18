import weaviate.classes.config as wvcc

weaviate_collection_config = {

    "class": "Development_Assistant_Document",
    "invertedIndexConfig": {
        "bm25": {
            "b": 0.75,
            "k1": 1.2
        },
        "cleanupIntervalSeconds": 60,
        "stopwords": {
            "additions": None,
            "preset": "en",
            "removals": None
        }
    },
    "multiTenancyConfig": {
        "autoTenantActivation": False,
        "autoTenantCreation": False,
        "enabled": False
    },
    "properties": [
        {
            "dataType": [
                wvcc.DataType.TEXT
            ],
            "description": "The content of the document",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "text",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "description": "Document Language",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "language",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "description": "The framework's help manual",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "framework",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "description": "This property specifies the title of document",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "title",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "description": "The source of the document",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "source",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "description": "The version of the franework",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "framework_ver",
            "tokenization": "word"
        },
        {
            "dataType": [
                "text"
            ],
            "description": "the summary of the document",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": True,
            "name": "description",
            "tokenization": "word"
        },
        {
            "dataType": [
                wvcc.DataType.DATE
            ],
            "description": "Document addition time",
            "indexFilterable": True,
            "indexRangeFilters": False,
            "indexSearchable": False,
            "name": "add_at"
        }
    ],
    "replicationConfig": {
        "asyncEnabled": False,
        "deletionStrategy": "NoAutomatedResolution",
        "factor": 1
    },
    "shardingConfig": {
        "actualCount": 1,
        "actualVirtualCount": 128,
        "desiredCount": 1,
        "desiredVirtualCount": 128,
        "function": "murmur3",
        "key": "_id",
        "strategy": "hash",
        "virtualPerPhysical": 128
    },
    "vectorIndexConfig": {
        "bq": {
            "enabled": False
        },
        "cleanupIntervalSeconds": 300,
        "distance": "cosine",
        "dynamicEfFactor": 8,
        "dynamicEfMax": 500,
        "dynamicEfMin": 100,
        "ef": -1,
        "efConstruction": 128,
        "filterStrategy": "sweeping",
        "flatSearchCutoff": 40000,
        "maxConnections": 32,
        "pq": {
            "bitCompression": False,
            "centroids": 256,
            "enabled": False,
            "encoder": {
                "distribution": "log-normal",
                "type": "kmeans"
            },
            "segments": 0,
            "trainingLimit": 100000
        },
        "skip": False,
        "sq": {
            "enabled": False,
            "rescoreLimit": 20,
            "trainingLimit": 100000
        },
        "vectorCacheMaxObjects": 1000000000000
    },
    "vectorIndexType": "hnsw",
    "vectorizer": "none",
    # "vectorConfig": {
    #     "dimensions": 1024  # 匹配BGE-m3模型
    # }
}
