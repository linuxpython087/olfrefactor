# processing/application/indexing/document_adapter.py

from langchain_core.documents import Document


class FactChunkDocumentAdapter:
    """
    Adapter strict :
    FactChunk -> LangChain Document
    """

    @staticmethod
    def to_document(chunk):
        return Document(
            page_content=chunk.text,  # UNIQUEMENT pour embedding
            metadata={"chunk_id": chunk.id, **chunk.payload},  # vérité complète
        )
