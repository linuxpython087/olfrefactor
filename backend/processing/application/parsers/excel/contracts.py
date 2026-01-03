from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# =========================
# NIVEAU 0 — INTROSPECTION
# =========================


@dataclass
class SheetIntrospection:
    name: str
    rows: int
    columns: int
    non_empty_ratio: float
    merged_cells_count: int
    empty_rows_top: int
    empty_rows_bottom: int


@dataclass
class ExcelIntrospection:
    file_size: int
    sheets: List[SheetIntrospection]


# =========================
# NIVEAU 1 — RAW
# =========================


@dataclass
class RawSheet:
    name: str
    matrix: List[List[Any]]


@dataclass
class RawWorkbook:
    sheets: Dict[str, RawSheet]


# =========================
# NIVEAU 2 — STRUCTURE
# =========================


@dataclass
class DetectedTable:
    sheet: str
    header_row: int
    data_start_row: int
    data_end_row: int
    columns: List[str]
    orientation: str  # "horizontal" | "vertical"
    confidence: float


@dataclass
class StructuredWorkbook:
    tables: List[DetectedTable]


# =========================
# NIVEAU 3 — NORMALISÉ
# =========================


@dataclass
class NormalizedTable:
    name: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    confidence: float


@dataclass
class NormalizedDocument:
    tables: List[NormalizedTable]


# processing/application/data_quality/contracts.py
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class QualityApprovedTable:
    name: str
    rows: List[Dict[str, Any]]
    confidence: float


@dataclass(frozen=True)
class QualityApprovedDocument:
    tables: List[QualityApprovedTable]
