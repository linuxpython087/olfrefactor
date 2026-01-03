from abc import ABC, abstractmethod
from typing import Optional

from processing.core.domaine.models import Extraction
from shared.value_objects import DocumentID, ExtractionID


class ExtractionRepository(ABC):
    @abstractmethod
    def save(self, extraction: Extraction) -> None:
        ...

    @abstractmethod
    def get_by_id(self, extraction_id: ExtractionID) -> Optional[Extraction]:
        ...

    @abstractmethod
    def get_by_document_id(self, document_id: DocumentID) -> Optional[Extraction]:
        ...
