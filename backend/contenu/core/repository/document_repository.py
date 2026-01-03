# backend/contenu/core/application/ports/document_repository.py
from abc import ABC, abstractmethod

from contenu.core.domaine.model import Document


class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> None:
        ...

    @abstractmethod
    def update(self, document: Document) -> None:
        ...

    @abstractmethod
    def get(self, document_id: str) -> Document | None:
        ...

    @abstractmethod
    def delete(self, document_id: str) -> None:
        ...
