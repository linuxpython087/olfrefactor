# tests/test_document.py
# tests/test_document.py
from datetime import datetime, timezone

import pytest
from contenu.core.domaine.events import (
    DocumentDeleteRequested,
    DocumentReadyForETL,
    DocumentStored,
    DocumentSubmitted,
    DocumentUploadStarted,
)
from contenu.core.domaine.model import Document
from shared.value_objects import DocumentID, TenantID, UserID


# =========================
# Fixtures
# =========================
@pytest.fixture
def document_id():
    return DocumentID.new()


@pytest.fixture
def user_id():
    return UserID.new()


@pytest.fixture
def tenant_id():
    return TenantID.new()


@pytest.fixture
def sample_document(document_id, user_id, tenant_id):
    return Document(
        id=document_id,
        submitted_by=user_id,
        filename="test.txt",
        size=1024,
        source_type="LOCAL",
    )


# =========================
# Tests
# =========================


def test_start_upload_emits_event(sample_document):
    doc = sample_document
    doc.start_upload()

    assert doc.status == "UPLOADING"
    events = doc.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], DocumentUploadStarted)
    assert events[0].document_id == doc.id


def test_mark_stored_emits_event(sample_document):
    doc = sample_document
    doc.start_upload()
    doc.pull_events()  # vider events intermédiaires

    uri = "https://dropbox.com/fake_path"
    checksum = "abc123"
    doc.mark_stored(uri, checksum)

    assert doc.status == "STORED"
    assert doc.storage_uri == uri
    assert doc.checksum == checksum

    events = doc.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], DocumentStored)
    assert events[0].storage_uri == uri
    assert events[0].checksum == checksum


def test_submit_emits_events(sample_document):
    doc = sample_document
    doc.start_upload()
    doc.mark_stored("uri", "checksum")
    doc.pull_events()  # vider events intermédiaires

    doc.submit()
    assert doc.status == "SUBMITTED"

    events = doc.pull_events()
    # 2 events: DocumentSubmitted + DocumentReadyForETL
    assert len(events) == 2
    assert isinstance(events[0], DocumentSubmitted)
    assert isinstance(events[1], DocumentReadyForETL)
    assert events[0].document_id == doc.id
    assert events[1].document_id == doc.id


def test_pull_events_clears_events(sample_document):
    doc = sample_document
    doc.start_upload()
    assert len(doc._events) == 1

    events = doc.pull_events()
    assert len(events) == 1
    # les événements sont maintenant vidés
    assert len(doc._events) == 0


def test_multiple_transitions(sample_document):
    doc = sample_document
    doc.start_upload()
    doc.mark_stored("uri", "checksum")
    doc.submit()

    assert doc.status == "SUBMITTED"

    events = doc.pull_events()
    types = [type(e) for e in events]
    assert DocumentUploadStarted in types
    assert DocumentStored in types
    assert DocumentSubmitted in types
    assert DocumentReadyForETL in types


def test_delete_requested_event(sample_document):
    doc = sample_document
    doc._raise(
        DocumentDeleteRequested(
            document_id=doc.id,
            requested_by=doc.submitted_by,
        )
    )
    events = doc.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], DocumentDeleteRequested)
    assert events[0].document_id == doc.id
