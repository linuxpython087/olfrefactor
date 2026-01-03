from typing import Any, List

from processing.application.parsers.excel.contracts import (
    DetectedTable,
    RawWorkbook,
    StructuredWorkbook,
)


class ExcelStructureAnalyzer:
    """
    Niveau 1 — Structure detection
    - Détection du header réel
    - Délimitation des données
    - ZÉRO logique métier
    """

    HEADER_THRESHOLD = 0.6
    FINAL_HEADER_THRESHOLD = 0.8
    MIN_NON_EMPTY_RATIO = 0.4
    MAX_SCAN_ROWS = 100

    # =========================
    # PUBLIC ENTRYPOINT
    # =========================

    @staticmethod
    def analyze(raw: RawWorkbook) -> StructuredWorkbook:
        tables = []

        for sheet_name, sheet in raw.sheets.items():
            matrix = sheet.matrix
            if not matrix:
                continue

            header_row, confidence = ExcelStructureAnalyzer._detect_final_header(matrix)

            if header_row is None:
                continue

            columns = ExcelStructureAnalyzer._extract_columns(matrix[header_row])
            data_start = header_row + 1
            data_end = ExcelStructureAnalyzer._find_data_end(matrix, data_start)

            tables.append(
                DetectedTable(
                    sheet=sheet_name,
                    header_row=header_row,
                    data_start_row=data_start,
                    data_end_row=data_end,
                    columns=columns,
                    orientation="horizontal",
                    confidence=confidence,
                )
            )

        return StructuredWorkbook(tables=tables)

    # =========================
    # HEADER DETECTION
    # =========================

    @staticmethod
    def _detect_final_header(matrix: List[List[Any]]):
        """
        Détecte le header FINAL (pas juste un candidat)
        """
        candidates = []

        scan_limit = min(len(matrix) - 1, ExcelStructureAnalyzer.MAX_SCAN_ROWS)

        for i in range(scan_limit):
            row = matrix[i]
            next_row = matrix[i + 1]

            score = ExcelStructureAnalyzer._header_likelihood_score(row)

            if score >= ExcelStructureAnalyzer.HEADER_THRESHOLD:
                candidates.append((i, score))

        for idx, score in candidates:
            row = matrix[idx]
            next_row = matrix[idx + 1]

            if ExcelStructureAnalyzer._is_final_header(row, next_row):
                return idx, score

        # fallback : meilleur score si aucun "final" détecté
        if candidates:
            return max(candidates, key=lambda x: x[1])

        return None, 0.0

    @staticmethod
    def _header_likelihood_score(row: List[Any]) -> float:
        """
        Probabilité qu'une ligne soit un header
        """
        non_empty = [c for c in row if c not in (None, "")]
        if len(non_empty) < 2:
            return 0.0

        string_count = sum(isinstance(c, str) for c in non_empty)
        numeric_count = sum(isinstance(c, (int, float)) for c in non_empty)

        score = string_count / len(non_empty)

        # bonus : labels courts
        avg_len = sum(len(str(c)) for c in non_empty if isinstance(c, str)) / max(
            string_count, 1
        )
        if avg_len < 30:
            score += 0.1

        # malus si trop numérique
        if numeric_count > string_count:
            score -= 0.2

        return max(0.0, min(score, 1.0))

    @staticmethod
    def _non_empty_ratio(row: List[Any]) -> float:
        non_empty = [c for c in row if c not in (None, "")]
        return len(non_empty) / max(len(row), 1)

    @staticmethod
    def _is_final_header(row: List[Any], next_row: List[Any]) -> bool:
        """
        Header FINAL = header fort suivi de données
        """
        return (
            ExcelStructureAnalyzer._header_likelihood_score(row)
            >= ExcelStructureAnalyzer.FINAL_HEADER_THRESHOLD
            and ExcelStructureAnalyzer._non_empty_ratio(row)
            >= ExcelStructureAnalyzer.MIN_NON_EMPTY_RATIO
            and ExcelStructureAnalyzer._header_likelihood_score(next_row) < 0.3
        )

    # =========================
    # COLUMNS & DATA RANGE
    # =========================

    @staticmethod
    def _extract_columns(row: List[Any]) -> List[str]:
        """
        Extraction safe des colonnes
        """
        columns = []

        for i, cell in enumerate(row):
            if isinstance(cell, str) and cell.strip():
                columns.append(cell.strip())
            else:
                columns.append(f"column_{i}")

        return columns

    @staticmethod
    def _find_data_end(matrix: List[List[Any]], start: int) -> int:
        """
        Fin des données = première ligne totalement vide
        """
        end = start

        for i in range(start, len(matrix)):
            if all(c in (None, "") for c in matrix[i]):
                break
            end = i

        return end
