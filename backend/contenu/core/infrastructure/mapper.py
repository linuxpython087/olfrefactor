# backend/contenu/core/infrastructure/mappers.py
from contenu.core.domaine.model import Document
from contenu.core.infrastructure.models import DocumentDB
from shared.enums import DocumentStatus, DocumentType
from shared.value_objects import DocumentID


class DocumentMapper:
    @staticmethod
    def to_model(doc: Document) -> DocumentDB:
        return DocumentDB(
            id=str(doc.id),
            submitted_by=str(doc.submitted_by),
            filename=doc.filename,
            size=doc.size,
            source_type=doc.source_type,
            storage_uri=doc.storage_uri,
            checksum=doc.checksum,
            status=doc.status.value,
            document_type=(doc.document_type.value if doc.document_type else None),
        )

    @staticmethod
    def from_model(model: DocumentDB) -> Document:
        return Document(
            id=model.id,
            submitted_by=DocumentID.from_string(str(model.submitted_by)),
            filename=model.filename,
            size=model.size,
            source_type=model.source_type,
            storage_uri=model.storage_uri,
            checksum=model.checksum,
            status=DocumentStatus(model.status),
            created_at=model.created_at,
            document_type=(
                DocumentType(model.document_type) if model.document_type else None
            ),
        )

    @staticmethod
    def to_dict(doc: Document) -> dict:
        return {
            "submitted_by": str(doc.submitted_by),
            "filename": doc.filename,
            "size": doc.size,
            "source_type": doc.source_type,
            "storage_uri": doc.storage_uri,
            "checksum": doc.checksum,
            "status": doc.status.value,
            "document_type": (doc.document_type.value if doc.document_type else None),
        }
