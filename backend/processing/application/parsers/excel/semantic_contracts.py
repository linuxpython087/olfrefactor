from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class SemanticColumn:
    name: str

    role: Literal[
        "country",
        "country_code",
        "indicator",
        "indicator_code",
        "year_value",
        "unknown",
    ]

    year: Optional[int] = None


from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class SemanticTable:
    name: str
    columns: List[SemanticColumn]
    rows: List[Dict[str, Any]]
    confidence: float


@dataclass
class SemanticDocument:
    tables: List[SemanticTable]
