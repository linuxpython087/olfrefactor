from processing.application.parsers.excel.contracts import (
    NormalizedDocument,
    NormalizedTable,
    RawWorkbook,
    StructuredWorkbook,
)
from processing.application.parsers.excel.introspector import ExcelIntrospection
from processing.application.parsers.excel.structure_analyzer import (
    ExcelStructureAnalyzer,
)


class ExcelNormalizer:
    @staticmethod
    def normalize(
        raw: RawWorkbook, structured: StructuredWorkbook
    ) -> NormalizedDocument:

        tables = []

        for table in structured.tables:
            sheet = raw.sheets[table.sheet]
            rows = []

            for r in range(table.data_start_row, table.data_end_row + 1):
                values = sheet.matrix[r]
                row_data = {}

                for idx, col in enumerate(table.columns):
                    row_data[col.lower()] = values[idx] if idx < len(values) else None

                if any(v not in (None, "") for v in row_data.values()):
                    rows.append(row_data)

            tables.append(
                NormalizedTable(
                    name=f"{table.sheet}_table",
                    columns=[c.lower() for c in table.columns],
                    rows=rows,
                    confidence=table.confidence,
                )
            )

        return NormalizedDocument(tables=tables)


import re
from typing import List

YEAR_COL_RE = re.compile(r"(19|20)\d{2}")


class TemporalUnpivotNormalizer:
    @staticmethod
    def normalize(doc: NormalizedDocument) -> NormalizedDocument:
        new_tables = []

        for table in doc.tables:
            static_cols = []
            year_cols = {}

            # 1️⃣ Identifier colonnes statiques vs temporelles
            for col in table.columns:
                match = YEAR_COL_RE.search(col)
                if match:
                    year = int(match.group())
                    year_cols[col] = year
                else:
                    static_cols.append(col)

            if not year_cols:
                new_tables.append(table)
                continue

            rows = []

            # 2️⃣ Déplier SANS PERTE
            for row in table.rows:
                for col, year in year_cols.items():
                    value = row.get(col)

                    # ⚠️ ON NE JETTE PAS 0
                    if value is None:
                        continue

                    new_row = {
                        **{c: row.get(c) for c in static_cols},
                        "year": year,
                        "value": value,
                    }
                    rows.append(new_row)

            new_tables.append(
                NormalizedTable(
                    name=table.name,
                    columns=static_cols + ["year", "value"],
                    rows=rows,
                    confidence=table.confidence,
                )
            )

        return NormalizedDocument(tables=new_tables)
