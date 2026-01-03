# backend/contenu/core/application/document_actions_service.py

from contenu.application.event_handlers import EventService
from contenu.core.domaine.model import Document
from contenu.core.repository.django_document_repository import DjangoDocumentRepository
from django.db import transaction
from shared.value_objects import UserID


class DocumentActionsService:
    """Service pour actions sur documents après soumission."""

    def __init__(
        self, repository: DjangoDocumentRepository, event_service: EventService
    ):
        self.repository = repository
        self.event_service = event_service

    @transaction.atomic
    def approve(self, doc_id: str, admin_id: UserID):
        doc = self.repository.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        doc.approve_document(admin_id)
        self.event_service.dispatch_events(doc.pull_events())
        self.repository.update(doc)
        return doc

    @transaction.atomic
    def reject(self, doc_id: str, admin_id: UserID, reason: str):
        doc = self.repository.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        doc.reject_document(admin_id, reason)
        self.event_service.dispatch_events(doc.pull_events())
        self.repository.update(doc)
        return doc

    @transaction.atomic
    def request_update(self, doc_id: str, user_id: UserID):
        doc = self.repository.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        doc.request_update(user_id)
        self.event_service.dispatch_events(doc.pull_events())
        self.repository.update(doc)
        return doc

    @transaction.atomic
    def request_delete(self, doc_id: str, user_id: UserID):
        doc = self.repository.get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        doc.request_delete(user_id)
        self.event_service.dispatch_events(doc.pull_events())
        self.repository.update(doc)
        return doc

    def escalate_pending(self, current_time):
        """Vérifie tous les documents SUBMITTED et escalade si > 48h"""
        docs = self.repository.get_all_submitted()
        for doc in docs:
            doc.escalate_if_not_validated(current_time)
            self.event_service.dispatch_events(doc.pull_events())
            self.repository.update(doc)
