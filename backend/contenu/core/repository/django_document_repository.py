# backend/contenu/core/infrastructure/repositories.py
from contenu.core.domaine.model import Document
from contenu.core.infrastructure.mapper import DocumentMapper
from contenu.core.infrastructure.models import DocumentDB
from contenu.core.repository.document_repository import DocumentRepository


class DjangoDocumentRepository(DocumentRepository):
    def save(self, document: Document) -> None:
        DocumentMapper.to_model(document).save(force_insert=True)

    def update(self, document: Document) -> None:
        DocumentDB.objects.filter(id=str(document.id)).update(
            storage_uri=document.storage_uri,
            checksum=document.checksum,
            status=document.status,
        )

    def get(self, document_id: str) -> Document | None:
        try:
            model = DocumentDB.objects.get(id=document_id)
            return DocumentMapper.from_model(model)
        except DocumentDB.DoesNotExist:
            return None

    def delete(self, document_id: str) -> None:
        DocumentDB.objects.filter(id=document_id).delete()
