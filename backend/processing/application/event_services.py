from typing import Callable, Dict, Type

from processing.core.domaine.events import (
    DomainEvent,
    ExtractionCompleted,
    ExtractionCreated,
    ExtractionFailed,
    ExtractionStarted,
    ExtractionValidated,
)

# Handlers d’exemple pour l’extraction


def log_extraction_created(event: ExtractionCreated):
    print(f"🚀 Extraction created for document {event.document_id}")


def log_extraction_started(event: ExtractionStarted):
    print(f"🚀 Extraction started for document {event.document_id}")


def log_extraction_completed(event: ExtractionCompleted):
    print(f"✅ Extraction completed for document {event.document_id}")


def log_extraction_failed(event: ExtractionFailed):
    print(f"❌ Extraction failed for document {event.document_id}: {event.error}")


def notify_admin_validation(event: ExtractionValidated):
    print(
        f"📨 Extraction validated by admin {event.admin_id} for document {event.document_id}"
    )


class EventServiceETL:
    """Service centralisé pour dispatcher les DomainEvents"""

    def __init__(self):
        self._handlers: Dict[Type, list[Callable]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Enregistrer les handlers par défaut pour l’extraction"""
        self.register(ExtractionCreated, log_extraction_created)
        self.register(ExtractionStarted, log_extraction_started)
        self.register(ExtractionCompleted, log_extraction_completed)
        self.register(ExtractionFailed, log_extraction_failed)
        self.register(ExtractionValidated, notify_admin_validation)

    def register(self, event_type: Type, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def handle_event(self, event: DomainEvent):
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"❌ Error handling {type(event).__name__}: {e}")

    def dispatch_events(self, events: list[DomainEvent]):
        for event in events:
            self.handle_event(event)
