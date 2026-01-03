import mimetypes
from pathlib import Path

from shared.enums import DocumentType


def detect_document_type(filename: str) -> DocumentType:
    ext = Path(filename).suffix.lower()

    if ext in [".xls", ".xlsx"]:
        return DocumentType.EXCEL
    if ext == ".pdf":
        return DocumentType.PDF
    if ext == ".csv":
        return DocumentType.CSV
    if ext in [".doc", ".docx"]:
        return DocumentType.WORD

    return DocumentType.UNKNOWN
