# backend/contenu/core/application/services.py

import hashlib
from typing import IO

from contenu.application.event_services import EventService
from contenu.core.domaine.model import Document
from contenu.core.repository.django_document_repository import DjangoDocumentRepository
from django.db import transaction
from uploader_and_downloader.dropbox_storage import DropboxStorage

CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB
import asyncio
from typing import IO, Protocol

from contenu.core.domaine.detect_document_type import detect_document_type
from processing.application.commands.create_extraction import (
    CreateExtraction,
    FailExtraction,
    RunExtraction,
    StartExtraction,
)
from processing.application.event_services import EventServiceETL
from processing.core.domaine.repositories.extraction_repository import (
    ExtractionRepository,
)


class HashProtocol(Protocol):
    def update(self, data: bytes) -> None:
        ...

    def hexdigest(self) -> str:
        ...


class StreamingFileWrapper:
    def __init__(self, file: IO[bytes], hasher: HashProtocol, on_progress=None):
        self.file = file
        self.hasher = hasher
        self.total_size = 0
        self.chunk_index = 0
        self.on_progress = on_progress

    def read(self, size: int = CHUNK_SIZE) -> bytes:
        chunk = self.file.read(size)
        if not chunk:
            return b""

        self.chunk_index += 1
        self.total_size += len(chunk)
        self.hasher.update(chunk)

        if self.on_progress:
            self.on_progress(self.chunk_index, self.total_size)

        return chunk


def log_progress(chunk_index, total_bytes):
    if chunk_index == 1 or chunk_index % 5 == 0:
        print(
            f"📊 Upload en cours | "
            f"{total_bytes/1024:.3f} KB transférés ({total_bytes/(1024*1024):.3f} MB)"
        )


import hashlib

from celery import shared_task


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_kwargs={"max_retries": 5},
)
def upload_document_task(self, document_id: str, temp_file_path: str):
    repository = DjangoDocumentRepository()
    storage = DropboxStorage()
    event_service = EventService()

    doc = repository.get(document_id)
    if not doc:
        raise RuntimeError("Document not found")

    doc.start_upload()
    doc.document_type = detect_document_type(doc.filename)

    hasher = hashlib.sha256()

    with open(temp_file_path, "rb") as f:
        stream = StreamingFileWrapper(f, hasher, on_progress=log_progress)

        uri = storage.upload(
            content=stream,
            filename=doc.filename,
            submitted_by=doc.submitted_by,
            document_id=doc.id,
        )

    checksum = hasher.hexdigest()

    doc.mark_stored(uri, checksum)
    doc.submit()

    events = doc.pull_events()
    event_service.dispatch_events(events)

    repository.update(doc)

    return {
        "document_id": doc.id,
        "uri": uri,
        "checksum": checksum,
    }


class DocumentService:
    def __init__(
        self,
        repository: DjangoDocumentRepository,
        storage: DropboxStorage,
        event_service: EventService,
    ):
        self.storage = storage
        self.repository = repository
        self.event_service = event_service

    @transaction.atomic
    def submit_document(self, doc: Document, file: IO[bytes]):
        print("\n🚀 [DocumentService] Début soumission document")
        doc.start_upload()
        doc.document_type = detect_document_type(doc.filename)

        hasher = hashlib.sha256()
        stream = StreamingFileWrapper(file, hasher, on_progress=log_progress)
        print("📄 Type détecté :", doc.document_type)

        print("☁️ Upload Dropbox + checksum en streaming…")

        uri = self.storage.upload(
            content=stream,
            filename=doc.filename,
            submitted_by=doc.submitted_by,
            document_id=doc.id,
        )

        checksum = hasher.hexdigest()

        print(
            f"✅ Upload terminé | "
            f"{stream.chunk_index} chunks | "
            f"Taille totale: {stream.total_size / 1024:.3f} KB "
            f"soit {stream.total_size / (1024 * 1024):.3f} MB"
        )

        print(f"🔐 Checksum SHA256: {checksum}")

        doc.mark_stored(uri, checksum)
        doc.submit()
        # dispatch events
        events = doc.pull_events()
        self.event_service.dispatch_events(events)

        print("💾 Persistance du document")
        existing_doc = self.repository.get(str(doc.id))
        if existing_doc:
            print("🔁 Document existant → update")
            self.repository.update(doc)
        else:
            print("🆕 Nouveau document → save")
            self.repository.save(doc)

        print("🎉 Soumission terminée avec succès\n")
        return doc
