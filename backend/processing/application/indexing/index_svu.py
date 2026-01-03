from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from processing.application.indexing.embeder_model import load_embedding_model
from processing.application.indexing.load_svu import load_svu
from processing.application.indexing.splitt_svu import split_svu_to_documents
from processing.application.indexing.vectore_store import (
    build_collection_name,
    create_vector_store_from_factchunks,
)
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

QDRANT_COLLECTION = "mapping_indicateurs_categories"


def index_svu():
    # 1. Charger la SVU
    svu = load_svu("./processing/application/indexing/svu.json")

    # 2. Split métier
    documents = split_svu_to_documents(svu)

    # 3. Embeddings
    embeddings = load_embedding_model()
    # 4. Qdrant client
    client = QdrantClient(host="qdrant", port=6333)

    # 5. Création / overwrite de la collection

    vector_size = len(embeddings.embed_query("sample text"))

    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings,
    )

    docs_ids = vectorstore.add_documents(documents=documents)

    print(f"✅ {len(docs_ids)} indicateurs indexés dans Qdrant")


if __name__ == "__main__":
    index_svu()
