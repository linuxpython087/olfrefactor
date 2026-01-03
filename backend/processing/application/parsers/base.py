from abc import ABC, abstractmethod
from typing import Any


class BaseDocumentParser(ABC):
    def __init__(self, document_id: str, content: bytes, filename: str):
        self.document_id = document_id
        self.content = content
        self.filename = filename

    @abstractmethod
    def parse(self) -> Any:
        """
        Retourne une structure NORMALISÉE brute :

        """
        ...
