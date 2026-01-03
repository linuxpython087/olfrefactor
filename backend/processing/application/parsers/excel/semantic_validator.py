from processing.application.parsers.excel.semantic_contracts import SemanticTable


class SemanticValidator:
    """
    Niveau 5 — Validation anti-bruit (Google-style)
    """

    @staticmethod
    def is_valid(table: SemanticTable) -> bool:
        roles = [c.role for c in table.columns]

        if roles.count("year_value") == 0:
            return False

        if roles.count("country") > 1:
            return False

        if roles.count("indicator") == 0:
            return False

        return True
