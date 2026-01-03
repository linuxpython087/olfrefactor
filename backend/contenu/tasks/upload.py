import logging

from celery import shared_task
from contenu.application.event_services import EventService
from contenu.application.services.stream import DocumentService
from contenu.core.repository.django_document_repository import DjangoDocumentRepository
from django.db import transaction
from uploader_and_downloader.dropbox_storage import DropboxStorage

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 30},
    retry_backoff=True,
    retry_jitter=True,
)
def submit_document_async(self, document_id: str):
    """
    Tâche asynchrone robuste :
    - upload streaming
    - hash
    - submit
    - events
    """

    logger.info(f"🚀 [Celery] Début submit_document_async {document_id}")

    repository = DjangoDocumentRepository()
    storage = DropboxStorage()
    event_service = EventService()

    service = DocumentService(
        repository=repository, storage=storage, event_service=event_service
    )

    doc = repository.get(document_id)
    if not doc:
        raise ValueError(f"Document {document_id} introuvable")

    with repository.get_file_stream(document_id) as file_stream:
        with transaction.atomic():
            service.submit_document(doc=doc, file=file_stream)

    logger.info(f"✅ [Celery] Document {document_id} soumis avec succès")
