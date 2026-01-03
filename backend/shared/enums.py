from enum import Enum


class DocumentType(Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    WORD = "word"
    JSON = "json"
    UNKNOWN = "unknown"


class DocumentStatus(Enum):
    # -------- DRAFT / UPLOAD --------
    DRAFT = "DRAFT"
    UPLOADING = "UPLOADING"
    STORED = "STORED"

    # -------- SUBMISSION --------
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

    # -------- UPDATE / DELETE --------
    UPDATE_REQUESTED = "UPDATE_REQUESTED"
    DELETE_REQUESTED = "DELETE_REQUESTED"

    # -------- ETL / PROCESSING --------
    READY_FOR_ETL = "READY_FOR_ETL"
    ETL_RUNNING = "ETL_RUNNING"
    PROCESSED = "PROCESSED"
    ETL_FAILED = "ETL_FAILED"
