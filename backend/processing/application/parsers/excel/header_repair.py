from dataclasses import dataclass
from typing import Any, Dict, List


class HeaderRepair:
    @staticmethod
    def merge_headers(matrix, header_row, data_start):
        headers = []
        for col in range(len(matrix[header_row])):
            parts = []
            for r in range(header_row, data_start):
                v = matrix[r][col]
                if isinstance(v, str):
                    parts.append(v.strip())
            headers.append(" ".join(parts))
        return headers


import re
import unicodedata


def normalize_key(k: str) -> str:
    k = unicodedata.normalize("NFKD", k).encode("ascii", "ignore").decode()
    k = k.lower()
    k = re.sub(r"%", "percent", k)
    k = re.sub(r"[^a-z0-9]+", "_", k)
    return k.strip("_")


def dedupe(keys):
    seen = {}
    out = []
    for k in keys:
        seen[k] = seen.get(k, 0) + 1
        out.append(k if seen[k] == 1 else f"{k}_{seen[k]}")
    return out


NULL_EQUIVALENTS = {None, "", "-", "N/A", "n/a"}


def clean_value(v):
    if v in NULL_EQUIVALENTS:
        return None
    if isinstance(v, str):
        v = v.strip()
        try:
            return float(v)
        except ValueError:
            return v
    return v


def is_metadata_row(row: dict) -> bool:
    str_ratio = sum(isinstance(v, str) for v in row.values()) / max(len(row), 1)
    return str_ratio > 0.8


def infer_type(values):
    nums = sum(isinstance(v, (int, float)) for v in values if v is not None)
    return "numeric" if nums / max(len(values), 1) > 0.8 else "string"


# excel/sanitizer/excel_sanitizer.py

# processing/application/parsers/excel/contracts.py


@dataclass
class SanitizedTable:
    name: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    column_types: Dict[str, str]
    confidence: float


@dataclass
class SanitizedDocument:
    tables: List[SanitizedTable]


from processing.application.parsers.excel.normalizer import ExcelNormalizer


class ExcelSanitizer:
    @staticmethod
    def sanitize(doc: ExcelNormalizer) -> SanitizedDocument:
        sanitized_tables = []

        for table in doc.tables:
            # 1️⃣ Normalize + dedupe headers
            normalized_cols = [normalize_key(c) for c in table.columns]
            normalized_cols = dedupe(normalized_cols)

            clean_rows = []
            column_values = {c: [] for c in normalized_cols}

            for row in table.rows:
                clean_row = {}

                for old_key, new_key in zip(table.columns, normalized_cols):
                    value = clean_value(row.get(old_key))
                    clean_row[new_key] = value
                    if value is not None:
                        column_values[new_key].append(value)

                # 2️⃣ Drop metadata rows
                if is_metadata_row(clean_row):
                    continue

                # 3️⃣ Drop fully empty rows
                if all(v is None for v in clean_row.values()):
                    continue

                clean_rows.append(clean_row)

            # 4️⃣ Infer column types
            column_types = {
                col: infer_type(vals) for col, vals in column_values.items()
            }

            sanitized_tables.append(
                SanitizedTable(
                    name=table.name,
                    columns=normalized_cols,
                    rows=clean_rows,
                    column_types=column_types,
                    confidence=table.confidence,
                )
            )

        return SanitizedDocument(tables=sanitized_tables)
