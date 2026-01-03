from processing.core.domaine.models import Extraction
from processing.core.infrastructure.models import ExtractionDB
from shared.extraction_status import ExtractionStatus
from shared.value_objects import DocumentID, ExtractionID


class ExtractionMapper:
    @staticmethod
    def to_domain(db: ExtractionDB) -> Extraction:
        extraction = Extraction(
            id=ExtractionID.from_string(db.id),
            document_id=DocumentID.from_string(db.document_id),
            status=ExtractionStatus(db.status),
            started_at=db.started_at,
            finished_at=db.finished_at,
            error=db.error,
        )
        return extraction

    @staticmethod
    def to_db(extraction: Extraction) -> ExtractionDB:
        return ExtractionDB(
            id=str(extraction.id),
            document_id=str(extraction.document_id),
            status=extraction.status.value,
            started_at=extraction.started_at,
            finished_at=extraction.finished_at,
            error=extraction.error,
        )
