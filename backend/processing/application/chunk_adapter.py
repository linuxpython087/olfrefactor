from langchain_core.documents import Document


def factchunk_to_document(chunk):
    return Document(
        page_content=chunk.text,  # pour embedding
        metadata={"id": chunk.id, **chunk.payload},
    )
