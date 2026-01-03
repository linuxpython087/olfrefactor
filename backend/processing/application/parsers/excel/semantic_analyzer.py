import re
from typing import List

from processing.application.parsers.excel.header_repair import SanitizedDocument
from processing.application.parsers.excel.semantic_contracts import (
    SemanticColumn,
    SemanticDocument,
    SemanticTable,
)


class SemanticTableAnalyzer:

    YEAR_REGEX = re.compile(r"(19|20)\d{2}")

    COUNTRY_KEYS = {"country", "nation", "state"}
    COUNTRY_CODE_KEYS = {"iso", "code", "country_code"}
    INDICATOR_KEYS = {"indicator", "series", "metric", "name"}
    INDICATOR_CODE_KEYS = {"indicator_code", "series_code", "code"}

    @staticmethod
    def analyze(doc: SanitizedDocument) -> SemanticDocument:
        semantic_tables = []

        for table in doc.tables:
            semantic_columns = []

            for col in table.columns:
                role, year = SemanticTableAnalyzer._infer_role(col, table)
                semantic_columns.append(SemanticColumn(name=col, role=role, year=year))

            semantic_tables.append(
                SemanticTable(
                    name=table.name,
                    columns=semantic_columns,
                    rows=table.rows,
                    confidence=table.confidence,
                )
            )

        return SemanticDocument(tables=semantic_tables)

    @staticmethod
    def _infer_role(column: str, table) -> tuple[str, int | None]:
        col_lower = column.lower()

        # YEAR
        match = SemanticTableAnalyzer.YEAR_REGEX.search(col_lower)
        if match:
            return "year_value", int(match.group())

        # COUNTRY
        if any(k in col_lower for k in SemanticTableAnalyzer.COUNTRY_KEYS):
            return "country", None

        # COUNTRY CODE
        if any(k in col_lower for k in SemanticTableAnalyzer.COUNTRY_CODE_KEYS):
            return "country_code", None

        # INDICATOR
        if any(k in col_lower for k in SemanticTableAnalyzer.INDICATOR_KEYS):
            return "indicator", None

        # INDICATOR CODE
        if any(k in col_lower for k in SemanticTableAnalyzer.INDICATOR_CODE_KEYS):
            return "indicator_code", None

        return "unknown", None
