from contenu.application.event_services import EventService
from contenu.application.services.stream import DocumentService
from contenu.core.domaine.dispatcher import EventDispatcher
from contenu.core.domaine.model import Document
from contenu.core.repository.django_document_repository import DjangoDocumentRepository
from uploader_and_downloader.dropbox_storage import DropboxStorage


def build_document_service():
    storage = DropboxStorage()
    event_service = EventService()
    repository = DjangoDocumentRepository()
    return DocumentService(
        storage=storage,
        repository=repository,
        event_service=event_service,
    )


from contenu.application.services.document_actions_services import (
    DocumentActionsService,
)
from contenu.core.repository.django_document_repository import DjangoDocumentRepository


def build_document_actions_service() -> DocumentActionsService:
    repository = DjangoDocumentRepository()
    event_service = EventService()
    return DocumentActionsService(repository=repository, event_service=event_service)
