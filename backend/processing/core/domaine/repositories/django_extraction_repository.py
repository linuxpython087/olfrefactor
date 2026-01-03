from typing import Optional

from django.db import transaction
from processing.core.domaine.models import Extraction
from processing.core.domaine.repositories.extraction_repository import (
    ExtractionRepository,
)
from processing.core.infrastructure.mappers import ExtractionMapper
from processing.core.infrastructure.models import ExtractionDB
from shared.value_objects import DocumentID, ExtractionID


class DjangoExtractionRepository(ExtractionRepository):
    @transaction.atomic
    def save(self, extraction: Extraction) -> None:
        ExtractionDB.objects.update_or_create(
            id=str(extraction.id),
            defaults={
                "document_id": str(extraction.document_id),
                "status": extraction.status.value,
                "started_at": extraction.started_at,
                "finished_at": extraction.finished_at,
                "error": extraction.error,
            },
        )

    def get_by_id(self, extraction_id: ExtractionID) -> Optional[Extraction]:
        try:
            db_obj = ExtractionDB.objects.get(id=str(extraction_id))
        except ExtractionDB.DoesNotExist:
            return None

        return ExtractionMapper.to_domain(db_obj)

    def get_by_document_id(self, document_id: DocumentID) -> Optional[Extraction]:
        try:
            db_obj = ExtractionDB.objects.get(document_id=str(document_id))
        except ExtractionDB.DoesNotExist:
            return None

        return ExtractionMapper.to_domain(db_obj)
