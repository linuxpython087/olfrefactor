import hashlib

from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from processing.core.infrastructure.model_category_indicator import Indicator
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    OptimizersConfigDiff,
    VectorParams,
)

QDRANT_COLLECTION = "svu_indicators_beat"


def indicator_point_id(indicator_id: str) -> int:
    h = hashlib.sha256(indicator_id.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def build_indicator_document(indicator) -> str:
    parts = [
        f"Indicator: {indicator.label}",
        f"Code: {indicator.indicator_code}",
        f"Category: {indicator.category.label}",
    ]

    if indicator.description:
        parts.append(f"Description: {indicator.description}")

    if indicator.value_type:
        parts.append(f"Value type: {indicator.value_type}")

    if indicator.unit:
        parts.append(f"Unit: {indicator.unit}")

    if indicator.aliases:
        parts.append("Aliases: " + ", ".join(indicator.aliases))

    if indicator.keywords:
        parts.append("Keywords: " + ", ".join(indicator.keywords))

    return " | ".join(parts)


class IndicatorIndexer:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

        self.vector_size = len(self.embeddings.embed_query("dimension_check"))

        self.client = QdrantClient(
            host="qdrant",
            port=6333,
        )

        self.disable_indexing = False

        if not self.client.collection_exists(QDRANT_COLLECTION):
            self.client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(m=0 if self.disable_indexing else 16),
                    on_disk=True,
                ),
                optimizers_config=OptimizersConfigDiff(
                    indexing_threshold=0 if self.disable_indexing else 20000
                ),
                shard_number=2,
            )

        self.vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=QDRANT_COLLECTION,
            embedding=self.embeddings,
        )

    def index_all(self):
        indicators = Indicator.objects.select_related("category").filter(is_active=True)

        texts = []
        metadatas = []
        ids = []

        for indicator in indicators:
            texts.append(build_indicator_document(indicator))
            metadatas.append(
                {
                    "indicator_id": indicator.indicator_id,
                    "indicator_code": indicator.indicator_code,
                    "label": indicator.label,
                    "category_code": indicator.category.code,
                    "category_label": indicator.category.label,
                    "value_type": indicator.value_type,
                    "unit": indicator.unit,
                    "aliases": indicator.aliases,
                    "keywords": indicator.keywords,
                    "source": "SVU",
                }
            )
            ids.append(indicator_point_id(indicator.indicator_id))

        self.vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
        )
