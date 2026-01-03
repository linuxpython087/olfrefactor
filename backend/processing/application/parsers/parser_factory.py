import os

from processing.application.parsers.base import BaseDocumentParser
from processing.application.parsers.excel.excel_parser import ExcelParser


class ParserFactory:
    @staticmethod
    def from_document(document_id, content: bytes, filename: str) -> BaseDocumentParser:
        ext = os.path.splitext(filename.lower())[1]

        if ext in [".xlsx", ".xls"]:
            return ExcelParser(document_id, content=content, filename=filename)

        raise ValueError(f"Aucun parser disponible pour {ext}")
