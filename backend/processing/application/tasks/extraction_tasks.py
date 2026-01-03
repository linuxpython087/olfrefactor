# processing/application/tasks/extraction_tasks.py

import logging

from celery import shared_task
from processing.application.services.extraction_pipeline import ExtractionPipeline
from processing.application.services.extraction_services import (
    ExtractionApplicationService,
)
from processing.core.domaine.repositories.django_extraction_repository import (
    DjangoExtractionRepository,
)
from shared.value_objects import DocumentID

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def run_extraction_pipeline(self, document_id: str):
    logger.info(f"[Celery] run_extraction_pipeline for document {document_id}")

    repository = DjangoExtractionRepository()
    service = ExtractionApplicationService(repository)
    pipeline = ExtractionPipeline()

    extraction = service.create_extraction(DocumentID.from_string(document_id))

    try:
        service.start_extraction(extraction)

        pipeline.run(
            extraction_id=str(extraction.id),
            document_id=document_id,
        )

        service.complete_extraction(extraction)

    except Exception as e:
        service.fail_extraction(extraction, str(e))
        raise
