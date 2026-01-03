from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ParsedDocument:
    """
    Résultat standardisé du parsing
    Quel que soit le type du document
    """

    metadata: Dict[str, Any]  # filename, source type, sheets, etc.
    tables: List[Dict[str, Any]]  # Chaque table contient rows et sheet_name
    raw_text: Optional[str] = None
