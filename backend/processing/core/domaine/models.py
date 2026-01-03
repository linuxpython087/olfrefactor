from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from processing.core.domaine.events import (
    DomainEvent,
    ExtractionCompleted,
    ExtractionCreated,
    ExtractionFailed,
    ExtractionStarted,
    ExtractionValidated,
)
from shared.exceptions import InvalidOperation
from shared.extraction_status import ExtractionStatus
from shared.value_objects import DocumentID, ExtractionID, UserID


@dataclass
class Extraction:
    id: ExtractionID
    document_id: DocumentID
    status: ExtractionStatus = field(
        default_factory=lambda: ExtractionStatus(ExtractionStatus.PENDING)
    )
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    error: Optional[str] = None

    _events: List[DomainEvent] = field(default_factory=list, init=False, repr=False, compare=False,)

    # ---------- FACTORY ----------
    @classmethod
    def create(cls, document_id: DocumentID) -> "Extraction":
        extraction = cls(
            id=ExtractionID.new(),
            document_id=document_id,
        )
        extraction._events.append(
            ExtractionCreated(
                extraction_id=extraction.id,
                document_id=extraction.document_id,
                occurred_at=datetime.now(timezone.utc),
            )
        )
        return extraction

    # ---------- BEHAVIOR ----------
    def start(self) -> None:
        if not self.status.can_start():
            raise InvalidOperation(
                f"Cannot start extraction in state {self.status.value}"
            )

        self.status = ExtractionStatus(ExtractionStatus.RUNNING)
        self.started_at = datetime.now(timezone.utc)

        self._events.append(
            ExtractionStarted(
                extraction_id=self.id,
                document_id=self.document_id,
                occurred_at=self.started_at,
            )
        )

    def complete(self) -> None:
        if not self.status.can_complete():
            raise InvalidOperation(
                f"Cannot complete extraction in state {self.status.value}"
            )

        self.status = ExtractionStatus(ExtractionStatus.EXTRACTED)
        self.finished_at = datetime.now(timezone.utc)

        self._events.append(
            ExtractionCompleted(
                extraction_id=self.id,
                document_id=self.document_id,
                occurred_at=self.finished_at,
            )
        )

    def fail(self, error: str) -> None:
        if not self.status.can_fail():
            raise InvalidOperation(
                f"Cannot fail extraction in state {self.status.value}"
            )

        self.status = ExtractionStatus(ExtractionStatus.FAILED)
        self.finished_at = datetime.now(timezone.utc)
        self.error = error

        self._events.append(
            ExtractionFailed(
                extraction_id=self.id,
                document_id=self.document_id,
                error=error,
                occurred_at=self.finished_at,
            )
        )

    def validate(self, admin_id: UserID) -> None:
        if not self.status.can_validate():
            raise InvalidOperation(
                f"Cannot validate extraction in state {self.status.value}"
            )

        self.status = ExtractionStatus(ExtractionStatus.VALIDATED)

        self._events.append(
            ExtractionValidated(
                extraction_id=self.id,
                document_id=self.document_id,
                admin_id=admin_id,
                occurred_at=datetime.now(timezone.utc),
            )
        )

    # ---------- EVENTS ----------
    def pull_events(self) -> List[DomainEvent]:
        events = self._events[:]
        self._events.clear()
        return events
