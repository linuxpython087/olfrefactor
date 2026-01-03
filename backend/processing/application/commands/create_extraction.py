# create_extraction.py

from processing.application.event_services import EventServiceETL
from processing.core.domaine.models import Extraction
from processing.core.domaine.repositories.extraction_repository import (
    ExtractionRepository,
)
from shared.value_objects import DocumentID, ExtractionID


class CreateExtraction:
    def __init__(self, repository: ExtractionRepository):
        self.repository = repository

    def execute(self, document_id: DocumentID) -> Extraction:
        # 🔍 Vérifier s'il existe déjà
        existing = self.repository.get_by_document_id(document_id)
        if existing:
            return existing  # ← IMPORTANT

        extraction = Extraction.create(document_id)
        self.repository.save(extraction)
        return extraction


class StartExtraction:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, extraction_id):
        extraction = self.repository.get_by_id(extraction_id)
        if extraction is None:
            raise ValueError("Extraction not found")

        extraction.start()
        self.repository.save(extraction)


class RunExtraction:
    def __init__(self, repository):
        self.repository = repository

    def execute(self, extraction_id: ExtractionID) -> None:
        extraction = self.repository.get_by_id(extraction_id)
        if extraction is None:
            raise ValueError("Extraction not found")

        # ici PAS de logique métier


# fail_extraction.py


class FailExtraction:
    def __init__(self, repository, dispatcher):
        self.repository = repository
        self.dispatcher = dispatcher

    def execute(self, extraction_id, error: str) -> None:
        extraction = self.repository.get_by_id(extraction_id)
        if extraction is None:
            raise ValueError("Extraction not found")

        extraction.fail(error)
        self.repository.save(extraction)
        self.dispatcher.dispatch(extraction.pull_events())


# validate_extraction.py

from shared.value_objects import UserID


class ValidateExtraction:
    def __init__(self, repository, dispatcher):
        self.repository = repository
        self.dispatcher = dispatcher

    def execute(self, extraction_id, admin_id: UserID) -> None:
        extraction = self.repository.get_by_id(extraction_id)
        if extraction is None:
            raise ValueError("Extraction not found")

        extraction.validate(admin_id)
        self.repository.save(extraction)
        self.dispatcher.dispatch(extraction.pull_events())


import asyncio
import logging

logger = logging.getLogger("etl.pipeline")
