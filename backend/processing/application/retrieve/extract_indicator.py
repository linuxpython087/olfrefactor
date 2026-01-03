import json
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document

# = == == == == == == == == == == == == == == == == == == == == == == == == == == == ==
# 1. Fonction pour extraire les données d'un document
# =========================================================


def extract_data_from_document(doc: Document) -> Dict[str, Any]:
    """
    Extrait les données d'un document selon votre structure.
    Priorité: metadata['payload'] > page_content['data']
    """
    data = {}

    # 1. Essayer depuis metadata['payload']
    payload = doc.metadata.get("payload")
    if payload and isinstance(payload, dict):
        data = payload.copy()

    # 2. Sinon, essayer depuis page_content
    if not data:
        try:
            content = json.loads(doc.page_content)
            if "data" in content:
                data = content["data"]
        except:
            pass

    # Ajouter les métadonnées source
    if data:
        data["_source"] = doc.metadata.get("source", {})
        data["_entity_type"] = doc.metadata.get("entity_type", "unknown")
        data["_chunk_id"] = doc.metadata.get("chunk_id", "")

    return data


# =========================================================
# 7. Fonction d'extraction directe (sans LLM)
# =========================================================


def direct_extraction(docs: List[Document]) -> List[Dict[str, Any]]:
    """
    Extraction directe sans LLM - parfaitement adaptée à votre cas
    puisque vous avez déjà les données structurées
    """
    print("\n🔍 EXTRACTION DIRECTE SANS LLM")
    print("   (Utilisation des données déjà structurées)")

    all_data = []

    for doc in docs:
        data = extract_data_from_document(doc)

        if data:
            # Nettoyer les champs de métadonnées si nécessaire
            cleaned_data = {k: v for k, v in data.items() if not k.startswith("_")}
            all_data.append(cleaned_data)

    print(f"✅ {len(all_data)} données extraites directement")

    return all_data
