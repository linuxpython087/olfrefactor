import logging

from processing.application.parsers.excel.semantic_contracts import (
    SemanticColumn,
    SemanticDocument,
    SemanticTable,
)

logger = logging.getLogger("etl.service")
import logging
import re
from typing import Any, Dict, List

import numpy as np

# ================================
# RÈGLES MÉTIER (CONFIGURABLES)
# ================================

REQUIRED_ROLES = {"country", "indicator", "year_value"}
MIN_NON_NULL_RATIO = 0.8
MIN_ROWS_PER_TABLE = 5


class SemanticDataCleaner:
    """
    Nettoyage sémantique avancé pour pipeline ETL robuste.
    Supprime réellement les lignes invalides conformément
    aux exigences client.
    """

    # ================================
    # API PRINCIPALE
    # ================================

    @staticmethod
    def clean_semantic_document(doc: "SemanticDocument") -> "SemanticDocument":
        cleaned_tables = []

        for table in doc.tables:
            cleaned_table = SemanticDataCleaner._clean_semantic_table(table)
            if cleaned_table:
                cleaned_tables.append(cleaned_table)

        return SemanticDocument(tables=cleaned_tables)

    # ================================
    # TABLE LEVEL
    # ================================

    @staticmethod
    def _clean_semantic_table(table: "SemanticTable") -> "SemanticTable | None":
        cleaned_rows = []

        for row in table.rows:
            cleaned_row = SemanticDataCleaner._clean_row(row, table.columns)

            if not SemanticDataCleaner._is_valid_row(cleaned_row, table.columns):
                continue

            if not SemanticDataCleaner._has_enough_data(cleaned_row):
                continue

            cleaned_rows.append(cleaned_row)

        if len(cleaned_rows) < MIN_ROWS_PER_TABLE:
            logger.warning(
                f"Table '{table.name}' ignorée (trop peu de lignes exploitables)"
            )
            return None

        return SemanticTable(
            name=table.name,
            columns=table.columns,
            rows=cleaned_rows,
            confidence=table.confidence,
        )

    # ================================
    # ROW LEVEL
    # ================================

    @staticmethod
    def _clean_row(row: dict, columns: list["SemanticColumn"]) -> dict:
        cleaned_row = {}

        for col in columns:
            original_value = row.get(col.name)
            cleaned_value = SemanticDataCleaner._clean_value(
                original_value, col.role, col.year
            )
            cleaned_row[col.name] = cleaned_value

        return cleaned_row

    @staticmethod
    def _is_valid_row(row: dict, columns: list["SemanticColumn"]) -> bool:
        """
        Vérifie que tous les champs critiques sont présents.
        """
        for col in columns:
            if col.role in REQUIRED_ROLES:
                if row.get(col.name) is None:
                    return False
        return True

    @staticmethod
    def _has_enough_data(row: dict) -> bool:
        """
        Vérifie le ratio de valeurs non nulles.
        """
        values = list(row.values())
        non_null_count = sum(v is not None for v in values)
        ratio = non_null_count / len(values)

        return ratio >= MIN_NON_NULL_RATIO

    # ================================
    # VALUE LEVEL
    # ================================

    @staticmethod
    def _clean_value(value: Any, role: str, year: int = None):
        if value is None:
            return None

        if role == "country":
            return SemanticDataCleaner._clean_country_value(value)

        elif role == "indicator":
            return SemanticDataCleaner._clean_indicator_value(value)

        elif role == "year_value":
            return SemanticDataCleaner._clean_year_value(value)

        elif role in {"country_code", "indicator_code"}:
            return SemanticDataCleaner._clean_code_value(value)

        return SemanticDataCleaner._clean_unknown_value(value)

    # ================================
    # ROLE-SPECIFIC CLEANERS
    # ================================

    @staticmethod
    def _clean_year_value(value):
        missing_values = {"..", "...", "NA", "N/A", "#N/A", "", "-", "--", "NaN", "nan"}

        if isinstance(value, str):
            value = value.strip()

            if value in missing_values:
                return None

            cleaned = re.sub(r"[^\d.-]", "", value)
            try:
                return float(cleaned) if cleaned else None
            except ValueError:
                return None

        if isinstance(value, (int, float)):
            return float(value)

        return None

    @staticmethod
    def _clean_country_value(value):
        if isinstance(value, str):
            return value.strip().title()
        return value

    @staticmethod
    def _clean_indicator_value(value):
        if isinstance(value, str):
            return re.sub(r"\s+", " ", value.strip())
        return value

    @staticmethod
    def _clean_code_value(value):
        if isinstance(value, str):
            return value.strip().upper().replace(" ", "")
        return value

    @staticmethod
    def _clean_unknown_value(value):
        if isinstance(value, str):
            return value.strip()
        return value
