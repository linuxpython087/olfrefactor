import logging

from contenu.core.repository.django_document_repository import DjangoDocumentRepository
from processing.application.commands.create_extraction import (
    CreateExtraction,
    FailExtraction,
    RunExtraction,
    StartExtraction,
)
from processing.application.services.document_etl_service import DocumentETLService
from shared.value_objects import DocumentID

logger = logging.getLogger("etl.pipeline")


class ExtractionPipeline:
    """
    Orchestrateur ETL SIMPLE
    Responsable du workflow complet
    """

    def __init__(
        self,
        create_uc: CreateExtraction,
        start_uc: StartExtraction,
        run_uc: RunExtraction,
        fail_uc: FailExtraction,
        repository,
    ):
        self.create_uc = create_uc
        self.start_uc = start_uc
        self.run_uc = run_uc
        self.fail_uc = fail_uc
        self.repository = repository
        self.document_repository = DjangoDocumentRepository()
        self.etl_service = DocumentETLService()

    def run(self, document_id: DocumentID) -> None:
        extraction = None

        try:
            logger.info(f"recherche de document {document_id}")
            document = self.document_repository.get(str(document_id))
            if not document:
                raise ValueError("Document introuvable")
            logger.info(
                f" Document {document_id} trouvé dont l'url est [{document.storage_uri}]"
            )
            # ---------- CREATE ----------
            extraction = self.create_uc.execute(document_id)
            logger.info(f"🆕 Extraction prête | id={extraction.id}")

            # ---------- START ----------
            self.start_uc.execute(extraction.id)
            extraction = self.repository.get_by_id(extraction.id)
            logger.info(f"🚀 Extraction démarrée | id={extraction.id}")

            # ---------- RUN ----------
            self.run_uc.execute(extraction.id)
            extraction = self.repository.get_by_id(extraction.id)
            logger.info(f"⚙️ Extraction exécutée | id={extraction.id}")

            logger.info("⚙️ Lancement du service ETL")
            self.etl_service.process(
                document_id=str(document.id),
                document_url=document.storage_uri,
                filename=document.filename,
            )

            # ---------- COMPLETE ----------
            extraction.complete()
            self.repository.save(extraction)
            logger.info(f"✅ Extraction complétée | id={extraction.id}")

        except Exception as e:
            logger.exception("❌ Erreur dans le pipeline ETL")

            if extraction and extraction.status.can_fail():
                self.fail_uc.execute(extraction.id, str(e))

            raise
