from datetime import datetime, timezone
from typing import List

from contenu.core.domaine.events import *
from shared.enums import DocumentStatus, DocumentType
from shared.exceptions import InvalidOperation
from shared.value_objects import DocumentID, TenantID, UserID


@dataclass
class Document:
    id: DocumentID
    submitted_by: UserID
    filename: str
    size: int
    source_type: str

    storage_uri: str | None = None
    checksum: str | None = None
    document_type: DocumentType | None = None

    status: DocumentStatus = DocumentStatus.DRAFT

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    _events: List[DomainEvent] = field(default_factory=list, init=False)

    # =========================
    # INTERNAL METHODS
    # =========================
    def _raise(self, event: DomainEvent):
        self._events.append(event)

    def pull_events(self) -> List[DomainEvent]:
        events = self._events[:]
        self._events.clear()
        return events

    # =========================
    # DOMAIN ACTIONS / COMMANDS
    # =========================
    def start_upload(self):
        if self.status != DocumentStatus.DRAFT:
            raise InvalidOperation(f"Upload not allowed in state {self.status.value}")

        self.status = DocumentStatus.UPLOADING

        self._raise(
            DocumentUploadStarted(
                document_id=self.id,
                submitted_by=self.submitted_by,
            )
        )

    def mark_stored(self, uri: str, checksum: str):
        if self.status != DocumentStatus.UPLOADING:
            raise InvalidOperation(
                f"Document must be UPLOADING, current={self.status.value}"
            )

        self.storage_uri = uri
        self.checksum = checksum
        self.status = DocumentStatus.STORED

        self._raise(
            DocumentStored(
                document_id=self.id,
                storage_uri=uri,
                checksum=checksum,
            )
        )

    def submit(self):
        if self.status != DocumentStatus.STORED:
            raise InvalidOperation(
                f"Document must be STORED, current={self.status.value}"
            )

        self.status = DocumentStatus.SUBMITTED

        self._raise(
            DocumentSubmitted(
                document_id=self.id,
                submitted_by=self.submitted_by,
            )
        )
        self._raise(
            DocumentReadyForETL(
                document_id=self.id,
            )
        )

    def request_update(self, requested_by: UserID):
        if self.status not in {
            DocumentStatus.SUBMITTED,
            DocumentStatus.PROCESSED,
        }:
            raise InvalidOperation(f"Update not allowed in state {self.status.value}")

        self.status = DocumentStatus.UPDATE_REQUESTED

        self._raise(
            DocumentUpdateRequested(
                document_id=self.id,
                requested_by=requested_by,
            )
        )

    def request_delete(self, requested_by: UserID):
        self.status = DocumentStatus.DELETE_REQUESTED
        self._raise(
            DocumentDeleteRequested(
                document_id=self.id,
                requested_by=requested_by,
            )
        )

    def approve_document(self, approved_by: UserID):
        if self.status != DocumentStatus.SUBMITTED:
            raise InvalidOperation(f"Cannot approve in state {self.status.value}")

        self.status = DocumentStatus.APPROVED

        self._raise(
            DocumentApproved(
                document_id=self.id,
                approved_by=approved_by,
                submitted_by=self.submitted_by,
            )
        )

    def reject_document(self, rejected_by: UserID, reason: str):
        if self.status != DocumentStatus.SUBMITTED:
            raise InvalidOperation(f"Cannot reject in state {self.status.value}")

        self.status = DocumentStatus.REJECTED

        self._raise(
            DocumentRejected(
                document_id=self.id,
                submitted_by=self.submitted_by,
                rejected_by=rejected_by,
                reason=reason,
            )
        )

    def escalate_if_not_validated(self, current_time: datetime):
        if self.status == DocumentStatus.SUBMITTED:
            delta = current_time - self.created_at

            if delta.total_seconds() > 48 * 3600:
                self.status = DocumentStatus.ESCALATED

                self._raise(
                    DocumentEscalated(
                        document_id=self.id,
                        submitted_by=self.submitted_by,
                    )
                )
