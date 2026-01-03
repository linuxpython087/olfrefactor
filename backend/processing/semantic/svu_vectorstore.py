# processing/semantic/svu_vectorstore.py

from langchain_qdrant import QdrantVectorStore
from processing.application.indexing.embeder_model import load_embedding_model
from qdrant_client import QdrantClient

QDRANT_COLLECTION = "mapping_indicateurs_categories"


def get_svu_vectorstore():
    client = QdrantClient(host="qdrant", port=6333)

    embeddings = load_embedding_model()  # ⚠️ EXACTEMENT le même

    return QdrantVectorStore(
        client=client, collection_name=QDRANT_COLLECTION, embedding=embeddings
    )
