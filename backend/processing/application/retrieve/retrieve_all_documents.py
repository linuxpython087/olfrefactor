import time
from typing import Dict, List

from langchain_core.documents import Document

# =========================================================
#  dump_all_facts
# =========================================================


def dump_all_facts(vector_store, collection_name, batch_size=500) -> List[Document]:
    client = vector_store.client
    docs = []
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        if not points:
            break

        for p in points:
            print("======================================")
            print(p)
            payload = p.payload
            # Le payload Qdrant contient TOUT, mais vous l'avez mal extrait
            # Dans Qdrant, vous avez stocké: metadata={"chunk_id": chunk.id, **chunk.payload}

            # Le payload contient les données dans page_content
            page_content = payload.get("page_content")
            metadata = payload.get("metadata", {})
            if page_content:
                # Le payload COMPLET est dans payload lui-même
                full_payload = payload

                # Mais attention: dans full_payload, il y a déjà "page_content" et "chunk_id"
                # Il faut extraire ce qui correspond au payload original

                # Le payload original est stocké sous les clés directes dans payload
                original_payload = {
                    "entity_type": metadata.get("entity_type"),
                    "source": metadata.get("source"),
                    "payload": metadata.get(
                        "payload"
                    ),  # C'est ICI que sont vos données
                    "provenance": metadata.get("provenance"),
                    "chunk_id": p.id,
                }

                docs.append(
                    Document(page_content=page_content, metadata=original_payload)
                )

        time.sleep(0.05)

        if not offset:
            break

    print(f"📦 {len(docs)} documents récupérés de la collection")
    return docs
