from abc import ABC, abstractmethod
from typing import IO
from uuid import UUID


class DocumentStorage(ABC):
    @abstractmethod
    def upload(self, *, content: IO[bytes], tenant_id: UUID, document_id: UUID) -> str:
        ...

    @abstractmethod
    def delete(self, storage_uri: str) -> None:
        ...

    @abstractmethod
    def compute_checksum(self, content: IO[bytes]) -> str:
        ...
