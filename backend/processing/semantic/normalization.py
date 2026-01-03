# processing/semantic/normalization.py

from typing import Any, Dict

META_FIELDS = {
    "annee",
    "year",
    "date",
    "pays",
    "country",
    "code_iso",
    "iso",
    "id",
    "uuid",
}


def normalize_field_name(name: str) -> str:
    return name.lower().replace("_", " ").replace("-", " ").strip()


def is_semantic_field(field_name: str) -> bool:
    return normalize_field_name(field_name) not in META_FIELDS


def extract_semantic_fields(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retire les champs non sémantiques AVANT RAG
    """
    return {k: v for k, v in row.items() if is_semantic_field(k)}
