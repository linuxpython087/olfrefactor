import io
from typing import Any, List

import pandas as pd
from processing.application.parsers.excel.contracts import RawSheet, RawWorkbook

# =========================
# CONSTANTES TECHNIQUES
# =========================

IGNORED_SHEET_NAMES = {
    "note",
    "notes",
    "instruction",
    "instructions",
    "readme",
    "read me",
    "about",
    "info",
    "code onu",
    "code onu_table",
    "code",
    "codes",
    "NOTES",
    "Code ONU",
}

EMPTY_MARKERS = {"...", "na", "n/a", "null", "none", "-", ".."}

# =========================
# RAW LOADER
# =========================


class ExcelRawLoader:
    """
    Parsing brut tolérant (ET – niveau 0).

    Responsabilités (Google-grade) :
    - Lecture Excel (I/O)
    - Conversion Pandas → Python natif
    - Normalisation TECHNIQUE des strings
    - Suppression UNIQUEMENT des lignes 100 % vides
    - ZÉRO interprétation métier
    """

    # -------------------------------------------------
    # SHEET FILTER
    # -------------------------------------------------

    @staticmethod
    def _should_ignore_sheet(sheet_name: str) -> bool:
        normalized = sheet_name.strip().lower()
        return normalized in IGNORED_SHEET_NAMES

    # -------------------------------------------------
    # STRING NORMALIZATION (TECHNIQUE)
    # -------------------------------------------------

    @staticmethod
    def _normalize_string(value: Any) -> Any:
        """
        Normalisation strictement technique :
        - suppression caractères invisibles
        - trim
        - mapping des marqueurs vides → None

        ❌ PAS de logique métier
        ❌ PAS de transformation sémantique
        """
        if not isinstance(value, str):
            return value

        cleaned = value.replace("\xa0", " ").replace("\u200b", "").strip()

        if not cleaned:
            return None

        if cleaned.lower() in EMPTY_MARKERS:
            return None

        return cleaned

    # -------------------------------------------------
    # ROW FILTER
    # -------------------------------------------------

    @staticmethod
    def _drop_fully_empty_rows(matrix: List[List[Any]]) -> List[List[Any]]:
        """
        Supprime UNIQUEMENT les lignes totalement vides.
        Une ligne est conservée dès qu'au moins une cellule est non nulle.
        """
        cleaned_rows = []

        for row in matrix:
            if any(cell is not None for cell in row):
                cleaned_rows.append(row)

        return cleaned_rows

    # -------------------------------------------------
    # MAIN LOADER
    # -------------------------------------------------

    @staticmethod
    def load(content: bytes) -> RawWorkbook:
        """
        Point d’entrée unique.
        """
        try:
            dfs = pd.read_excel(
                io.BytesIO(content),
                sheet_name=None,
                header=None,
                dtype=object,
                engine="openpyxl",
            )
        except Exception as exc:
            raise RuntimeError(f"Pandas failed to load Excel: {exc}") from exc

        sheets = {}

        for sheet_name, df in dfs.items():
            if ExcelRawLoader._should_ignore_sheet(sheet_name):
                continue

            # Pandas → Python (NaN → None)
            matrix = df.where(pd.notnull(df), None).values.tolist()

            # Normalisation TECHNIQUE cellule par cellule
            matrix = [
                [ExcelRawLoader._normalize_string(cell) for cell in row]
                for row in matrix
            ]

            # Suppression des lignes 100 % vides
            matrix = ExcelRawLoader._drop_fully_empty_rows(matrix)

            if not matrix:
                continue

            sheets[sheet_name] = RawSheet(
                name=sheet_name,
                matrix=matrix,
            )

        return RawWorkbook(sheets=sheets)
