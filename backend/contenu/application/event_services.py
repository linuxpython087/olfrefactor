# backend/contenu/core/application/event_service.py
from typing import Callable, Dict, Type

from contenu.core.domaine.events import *
from contenu.tasks.emails import (
    notify_admin_approval_task,
    notify_admin_task,
    notify_user_rejection_task,
)
from contenu.tasks.etl import run_etl_pipeline_task
from contenu.tasks.logs import log_upload_started_task
from contenu.tasks.maintenance import escalate_to_sysadmin_task


class EventService:
    """Service centralisé pour dispatcher les DomainEvents (ASYNC ONLY)"""

    def __init__(self):
        self._handlers: Dict[Type, list[Callable]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        self.register(DocumentSubmitted, self._on_document_submitted)
        self.register(DocumentReadyForETL, self._on_document_ready_for_etl)
        self.register(DocumentUploadStarted, self._on_upload_started)
        self.register(DocumentApproved, self._on_document_approved)
        self.register(DocumentRejected, self._on_document_rejected)
        self.register(DocumentEscalated, self._on_document_escalated)

    # =========================
    # EVENT → CELERY ADAPTERS
    # =========================

    def _on_document_submitted(self, event: DocumentSubmitted):
        notify_admin_task.delay(
            document_id=str(event.document_id),
            submitted_by=str(event.submitted_by),
        )

    def _on_document_ready_for_etl(self, event: DocumentReadyForETL):
        run_etl_pipeline_task.delay(document_id=str(event.document_id))

    def _on_upload_started(self, event: DocumentUploadStarted):
        log_upload_started_task.delay(
            document_id=str(event.document_id),
            submitted_by=str(event.submitted_by),
        )

    def _on_document_approved(self, event: DocumentApproved):
        notify_admin_approval_task.delay(
            document_id=str(event.document_id),
            approved_by=str(event.approved_by),
        )

    def _on_document_rejected(self, event: DocumentRejected):
        notify_user_rejection_task.delay(
            document_id=str(event.document_id),
            rejected_by=str(event.rejected_by),
            reason=event.reason,
        )

    def _on_document_escalated(self, event: DocumentEscalated):
        escalate_to_sysadmin_task.delay(
            document_id=str(event.document_id),
            reason=event.reason,
        )

    # =========================
    # CORE DISPATCH
    # =========================

    def register(self, event_type: Type, handler: Callable):
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch_events(self, events: list):
        for event in events:
            for handler in self._handlers.get(type(event), []):
                try:
                    handler(event)
                except Exception as e:
                    print(
                        f"❌ Erreur handler {handler.__name__} "
                        f"pour {type(event).__name__}: {e}"
                    )
