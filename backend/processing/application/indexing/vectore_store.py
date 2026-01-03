import logging
import uuid
from datetime import datetime
from typing import Iterable, List

from langchain_qdrant import QdrantVectorStore
from processing.application.indexing.document_adapter import FactChunkDocumentAdapter
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    HnswConfigDiff,
    OptimizersConfigDiff,
    VectorParams,
)

logger = logging.getLogger(__name__)


# =============================
# Utils
# =============================
def build_collection_name(filename: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:6]
    return f"{filename}_{ts}_{uid}"


def chunked(iterable: List, batch_size: int):
    for i in range(0, len(iterable), batch_size):
        yield iterable[i : i + batch_size]


# =============================
# Core Indexing Function
# =============================
def create_vector_store_from_factchunks(
    chunks: Iterable,
    embeddings,
    collection_name: str,
    *,
    batch_size: int = 500,
    disable_indexing: bool = True,
) -> QdrantVectorStore:
    """
    Google-grade vector indexing pipeline.

    - Safe ingestion mode
    - Fast bulk upload
    - Deferred HNSW indexing
    - Architecture-preserving
    """

    logger.info("⚡ Initializing Qdrant client")
    client = QdrantClient(host="qdrant", port=6333)

    logger.info("📐 Detecting embedding vector size")
    vector_size = len(embeddings.embed_query("dimension_check"))

    # =============================
    # 1️⃣ Create collection (INGESTION MODE)
    # =============================
    logger.info("🧱 Creating collection in ingestion mode")
    if not client.collection_exists(collection_name):

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(m=0 if disable_indexing else 16),
                on_disk=True,  # ✅ safe for large volumes
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=0 if disable_indexing else 20000
            ),
            shard_number=2,  # ✅ parallel ingestion
        )

    store = QdrantVectorStore(
        client=client, collection_name=collection_name, embedding=embeddings
    )

    # =============================
    # 2️⃣ Prepare documents
    # =============================
    logger.info("🔄 Adapting FactChunks to Documents")

    documents = [FactChunkDocumentAdapter.to_document(chunk) for chunk in chunks]

    logger.info(f"📦 Total documents to index: {len(documents)}")

    # =============================
    # 3️⃣ Batched upload
    # =============================
    indexed = 0
    for batch in chunked(documents, batch_size):
        store.add_documents(batch)
        indexed += len(batch)
        logger.info(f"🚚 Indexed {indexed}/{len(documents)} documents")

    # =============================
    # 4️⃣ Re-enable indexing (POST INGESTION)
    # =============================
    if disable_indexing:
        logger.info("🔧 Re-enabling HNSW indexing")

        client.update_collection(
            collection_name=collection_name,
            hnsw_config=HnswConfigDiff(m=16),
            optimizers_config=OptimizersConfigDiff(indexing_threshold=20000),
        )

    logger.info(f"✅ Collection ready: {collection_name}")
    return store
