import logging

from decouple import config
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

OPENAI_API_KEY = config("OPENAI_API_KEY")

QDRANT_COLLECTION = "mapping_indicateurs_categories"

EMBEDDING_MODEL = "text-embedding-3-large"

import logging
import time
from typing import Any, Dict, List

from qdrant_client.http.exceptions import UnexpectedResponse


def batch_classify_fields(
    field_names: List[str],
    user_tier: int = 1,
    context: dict | None = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:

    results: List[Dict[str, Any]] = []

    max_retries = 6
    delay_increment = 60
    batch_size = min(30 if user_tier < 4 else 80, len(field_names))
    logging.info(f"[RAG] Batch size = {batch_size}")

    for i in range(0, len(field_names), batch_size):
        batch = field_names[i : i + batch_size]
        logging.info(f"[RAG] Processing batch index {i}")

        retries = 0
        while retries <= max_retries:
            try:
                for field in batch:
                    matches = classify_field(field_name=field, top_k=top_k)

                    # 🔑 FORMAT IDENTIQUE À classify_field
                    results.append({"field_name": field, "matches": matches or []})

                break  # succès

            except Exception as e:
                msg = str(e).lower()
                if "rate limit" in msg or "429" in msg:
                    delay = (retries + 1) * delay_increment
                    logging.warning(f"[RAG] Rate limit detected. Retrying in {delay}s")
                    time.sleep(delay)
                    retries += 1
                else:
                    logging.error(f"[RAG] Fatal error: {e}")
                    break

        if retries > max_retries:
            logging.error(f"[RAG] Max retries exceeded for batch starting at {i}")

    logging.info(f"[RAG] Total classified fields: {len(results)}")
    return results


def classify_field(field_name: str, top_k: int = 3):
    """
    Classe un champ extrait vers la SVU
    """
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)

    client = QdrantClient(host="qdrant", port=6333)

    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=QDRANT_COLLECTION,
        embedding=embeddings,
    )

    # Texte métier à comparer
    query = field_name.replace("_", " ")

    results = vectorstore.similarity_search_with_score(query=query, k=top_k)

    matches = []
    for doc, score in results:
        matches.append(
            {
                "indicator_id": doc.metadata["indicator_id"],
                "indicator_code": doc.metadata["indicator_code"],
                "category": doc.metadata["category"],
                "unit": doc.metadata.get("unit"),
                "score": float(score),
                "description": doc.page_content,
            }
        )

    return matches


# ============================================================
# 🔒 SINGLETON VECTORSTORE
# ============================================================

_embeddings = None
_vectorstore = None


def get_vectorstore():
    global _embeddings, _vectorstore

    if _vectorstore is None:
        _embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY
        )

        client = QdrantClient(host="qdrant", port=6333)

        _vectorstore = QdrantVectorStore(
            client=client,
            collection_name=QDRANT_COLLECTION,
            embedding=_embeddings,
        )

    return _vectorstore


# ============================================================
# 🧠 CONSTRUCTION REQUÊTE SÉMANTIQUE
# ============================================================

FORBIDDEN_FIELDS = {"value", "val", "number", "nombre", "montant", "total"}


def build_semantic_query(field: str, context: dict | None = None) -> str | None:
    """
    Construit une requête sémantique métier robuste
    Retourne None si le champ est inutilisable
    """

    if not field:
        return None

    field_norm = field.lower().strip()

    # 🚫 BLOQUANT : champs sans sémantique
    if field_norm in FORBIDDEN_FIELDS:
        return None

    parts = []

    # champ principal
    parts.append(field.replace("_", " "))

    # heuristiques métier
    if "%" in field or "percent" in field or "taux" in field:
        parts.append("pourcentage taux ratio")

    if "growth" in field or "croissance" in field:
        parts.append("croissance evolution annuelle")

    if "population" in field or "habitants" in field:
        parts.append("population demographie")

    if "pib" in field or "gdp" in field:
        parts.append("produit interieur brut economie")

    if "francophone" in field:
        parts.append("langue francaise locuteurs")

    # contexte léger (⚠️ jamais dominant)
    if context:
        if context.get("country"):
            parts.append(f"pays {context['country']}")
        if context.get("year"):
            parts.append(f"annee {context['year']}")

    return " ".join(parts)


# ============================================================
# 🔍 CLASSIFICATION PAR LOT
# ============================================================


def classify_fields_batch(
    fields,
    context: dict | None = None,
    top_k: int = 3,
    batch_size: int = 32,
    verbose: bool = True,
):
    """
    fields : iterable (list / set / dict_keys)
    """
    vectorstore = get_vectorstore()
    all_results = {}

    fields = list(fields)
    total = len(fields)
    processed = 0

    if total == 0:
        return all_results

    total_batches = (total + batch_size - 1) // batch_size

    for batch_idx in range(0, total, batch_size):
        batch_number = (batch_idx // batch_size) + 1
        batch = fields[batch_idx : batch_idx + batch_size]

        if verbose:
            print(
                f"\n[Batch {batch_number}/{total_batches}] "
                f"Traitement champs {batch_idx} → {batch_idx + len(batch) - 1}"
            )

        for field in batch:
            query = build_semantic_query(field, context)

            # 🚫 skip champs non exploitables
            if query is None:
                if verbose:
                    print(f"  ⏭️  skip champ non sémantique : {field}")
                continue

            results = vectorstore.similarity_search_with_score(query=query, k=top_k)

            logger.info(f"results: {results}")

            formatted = []
            for doc, score in results:
                formatted.append(
                    {
                        "indicator_id": doc.metadata.get("indicator_id"),
                        "indicator_code": doc.metadata.get("indicator_code"),
                        "category": doc.metadata.get("category"),
                        "unit": doc.metadata.get("unit"),
                        "score": round(float(score), 4),
                        "description": doc.page_content,
                    }
                )

            all_results[field] = formatted
            processed += 1

            if verbose:
                percent = (processed / total) * 100
                print(f"  [{processed}/{total} | {percent:.1f}%] {field}")

    if verbose:
        print("\n✅ Classification terminée.")

    return all_results


# ============================================================
# 🔒 CONSTANTES
# ============================================================

META_KEYS = {
    "pays",
    "country",
    "country_name",
    "nom_pays",
    "code_iso",
    "country_code",
    "geounit",
    "année",
    "year",
    "date",
    "time",
    "région",
    "region",
}

FORBIDDEN_FIELDS = {"value", "val", "nombre", "total", "montant"}

# ============================================================
# 🧠 SCHEMA DETECTION (UNIVERSEL)
# ============================================================


def detect_schema_universal(row: dict) -> str:
    """
    Détecte l'intention sémantique d'une ligne
    Totalement indépendante du format
    """

    if not isinstance(row, dict) or not row:
        return "unknown"

    keys = {k.lower() for k in row.keys()}
    values = list(row.values())

    numeric_values = [v for v in values if isinstance(v, (int, float))]

    # ---------- TIME SERIES ----------
    has_time = any(k in keys for k in {"year", "année", "date", "time"})
    has_indicator = any(
        k in keys
        for k in {
            "series_name",
            "indicator",
            "indicator_name",
            "nom_indicateur",
            "libelle",
            "label",
        }
    )

    if has_time and has_indicator and len(numeric_values) == 1:
        return "time_series"

    # ---------- COUNTRY SNAPSHOT ----------
    has_country = any(
        k in keys for k in {"country", "country_name", "pays", "nom_pays"}
    )

    if has_country and len(numeric_values) >= 2:
        return "country_snapshot"

    # ---------- METADATA ----------
    if len(numeric_values) == 0:
        return "metadata"

    return "unknown"


# ============================================================
# 🔄 NORMALISATION UNIVERSELLE
# ============================================================


def normalize_row_universal(row: dict) -> dict:
    """
    Transforme une ligne brute en structure contractuelle
    """

    schema = detect_schema_universal(row)

    normalized = {
        "schema": schema,
        "country": (
            row.get("pays")
            or row.get("country_name")
            or row.get("country")
            or row.get("nom_pays")
        ),
        "code_iso": (
            row.get("code_iso") or row.get("country_code") or row.get("geounit")
        ),
        "year": (row.get("année") or row.get("year")),
        "fields": {},
    }

    # ---------- TIME SERIES ----------
    if schema == "time_series":
        for k, v in row.items():
            if isinstance(v, (int, float)):
                indicator_name = (
                    row.get("series_name")
                    or row.get("indicator")
                    or row.get("indicator_name")
                    or row.get("nom_indicateur")
                )
                if indicator_name:
                    normalized["fields"][indicator_name] = v
                break

        return normalized

    # ---------- COUNTRY SNAPSHOT ----------
    if schema == "country_snapshot":
        for k, v in row.items():
            if k.lower() in META_KEYS:
                continue
            if k.lower() in FORBIDDEN_FIELDS:
                continue
            if not isinstance(v, (int, float)):
                continue

            normalized["fields"][k] = v

        return normalized

    # ---------- AUTRES ----------
    return normalized


# ============================================================
# 🔍 CLASSIFICATION UNIVERSELLE
# ============================================================


def classify_any_row(
    row: dict, score_threshold: float = 0.45, top_k: int = 3
) -> List[Dict[str, Any]]:

    normalized = normalize_row_universal(row)

    if not normalized["fields"]:
        return []

    field_names = list(normalized["fields"].keys())

    rag_results = batch_classify_fields(
        field_names=field_names,
        context={"country": normalized["country"], "year": normalized["year"]},
        top_k=top_k,
    )

    logger.info(f"classify_any_row : {rag_results}")

    rag_map = {r["field_name"]: r["matches"] for r in rag_results}

    results = []

    for field, value in normalized["fields"].items():
        matches = rag_map.get(field)
        if not matches:
            continue

        best = matches[0]

        record = {
            "schema": normalized["schema"],
            "country": normalized["country"],
            "code_iso": normalized["code_iso"],
            "year": normalized["year"],
            "raw_field": field,
            "raw_value": value,
            "best_match": None,
            "candidates": [],
        }

        for m in matches:
            record["candidates"].append(
                {
                    "indicator_id": m["indicator_id"],
                    "indicator_code": m["indicator_code"],
                    "category": m["category"],
                    "unit": m["unit"],
                    "score": round(m["score"], 3),
                }
            )

        if best["score"] >= score_threshold:
            record["best_match"] = {
                "indicator_id": best["indicator_id"],
                "indicator_code": best["indicator_code"],
                "category": best["category"],
                "unit": best["unit"],
                "confidence_score": round(best["score"], 3),
            }

        results.append(record)

        logger.info(f"classify_any_row : {results}")

    return results


# ============================================================
# 🌍 DATASET GLOBAL
# ============================================================


def process_dataset_global(dataset: List[dict]) -> List[dict]:
    all_results = []

    for row in dataset:
        all_results.extend(classify_any_row(row))

    return all_results


# ============================================================
