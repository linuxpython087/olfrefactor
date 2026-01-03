from dataclasses import dataclass, field
from datetime import datetime, timezone

from shared.value_objects import DocumentID, TenantID, UserID


@dataclass(frozen=True)
class DomainEvent:
    occurred_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc), init=False
    )


# -------------------------
# Events
# -------------------------
@dataclass(frozen=True)
class DocumentUploadStarted(DomainEvent):
    document_id: DocumentID
    submitted_by: UserID


@dataclass(frozen=True)
class DocumentStored(DomainEvent):
    document_id: DocumentID
    storage_uri: str
    checksum: str


@dataclass(frozen=True)
class DocumentSubmitted(DomainEvent):
    document_id: DocumentID
    submitted_by: UserID


@dataclass(frozen=True)
class DocumentApproved(DomainEvent):
    document_id: DocumentID
    submitted_by: UserID
    approved_by: UserID


@dataclass(frozen=True)
class DocumentRejected(DomainEvent):
    document_id: DocumentID
    submitted_by: UserID
    rejected_by: UserID
    reason: str


@dataclass(frozen=True)
class DocumentEscalated(DomainEvent):
    document_id: DocumentID
    submitted_by: UserID
    reason: str = "48h non validé"


@dataclass(frozen=True)
class DocumentDeleteRequested(DomainEvent):
    document_id: DocumentID
    requested_by: UserID


@dataclass(frozen=True)
class DocumentUpdateRequested(DomainEvent):
    document_id: DocumentID
    requested_by: UserID


@dataclass(frozen=True)
class DocumentReadyForETL(DomainEvent):
    document_id: DocumentID
