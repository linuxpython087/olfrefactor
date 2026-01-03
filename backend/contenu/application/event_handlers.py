# backend/contenu/core/application/event_service.py
from typing import Callable, Dict, Type

from celery import shared_task
from contenu.core.domaine.events import *


# Exemple: notifier l'admin
def notify_admin(event: DocumentSubmitted):
    print(
        f"📨 Notification admin: Document {event.document_id} soumis par {event.submitted_by}"
    )


# Exemple: déclencher l'ETL
def trigger_etl(event: DocumentReadyForETL):
    print(f"⚙️ ETL déclenché pour le document {event.document_id}")


# Exemple: log simple
def log_upload_started(event: DocumentUploadStarted):
    print(f"🚀 Upload démarré pour {event.document_id} par {event.submitted_by}")


def notify_admin_approval(event: DocumentApproved):
    print(f"✅ Document {event.document_id} approuvé par {event.approved_by}")


def notify_user_rejection(event: DocumentRejected):
    print(
        f"❌ Document {event.document_id} rejeté par {event.rejected_by} (raison: {event.reason})"
    )


def escalate_to_sysadmin(event: DocumentEscalated):
    print(
        f"⚠️ Document {event.document_id} non validé après 48h → Escalade au sysadmin"
    )


class EventService:
    """Service centralisé pour dispatcher les DomainEvents"""

    def __init__(self):
        self._handlers: Dict[Type, list[Callable]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Enregistrer les handlers par défaut"""
        self.register(DocumentSubmitted, notify_admin)
        self.register(DocumentReadyForETL, trigger_etl)
        self.register(DocumentUploadStarted, log_upload_started)
        self.register(DocumentApproved, notify_admin_approval)
        self.register(DocumentRejected, notify_user_rejection)
        self.register(DocumentEscalated, escalate_to_sysadmin)

    def register(self, event_type: Type, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def handle_event(self, event):
        """Dispatch un événement à tous les handlers enregistrés"""
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(
                    f"❌ Erreur lors du traitement de l'événement {type(event).__name__}: {e}"
                )

    def dispatch_events(self, events: list):
        for event in events:
            self.handle_event(event)
