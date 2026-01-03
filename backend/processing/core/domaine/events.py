from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainEvent:
    occurred_at: datetime


from dataclasses import dataclass
from datetime import datetime

from shared.value_objects import DocumentID, ExtractionID, UserID


@dataclass
class ExtractionStarted(DomainEvent):
    extraction_id: ExtractionID
    document_id: DocumentID


@dataclass
class ExtractionCompleted(DomainEvent):
    extraction_id: ExtractionID
    document_id: DocumentID


@dataclass
class ExtractionFailed(DomainEvent):
    extraction_id: ExtractionID
    document_id: DocumentID
    error: str


@dataclass
class ExtractionValidated(DomainEvent):
    extraction_id: ExtractionID
    document_id: DocumentID
    admin_id: UserID


@dataclass
class ExtractionCreated(DomainEvent):
    extraction_id: ExtractionID
    document_id: DocumentID
    occurred_at: datetime
