from datetime import datetime, timezone

import pytest
from processing.core.domaine.events import (
    ExtractionCompleted,
    ExtractionFailed,
    ExtractionStarted,
    ExtractionValidated,
)
from processing.core.domaine.models import Extraction
from shared.exceptions import InvalidOperation
from shared.extraction_status import ExtractionStatus
from shared.value_objects import DocumentID, UserID


def test_create_extraction():
    document_id = DocumentID.new()

    extraction = Extraction.create(document_id)

    assert extraction.document_id == document_id
    assert extraction.status.value == ExtractionStatus.PENDING
    assert extraction.started_at is None
    assert extraction.finished_at is None


def test_start_extraction():
    extraction = Extraction.create(DocumentID.new())
    extraction.pull_events()

    extraction.start()

    assert extraction.status.value == ExtractionStatus.RUNNING
    assert extraction.started_at is not None

    events = extraction.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], ExtractionStarted)


def test_cannot_start_twice():
    extraction = Extraction.create(DocumentID.new())
    extraction.pull_events()

    extraction.start()

    with pytest.raises(InvalidOperation):
        extraction.start()


def test_complete_extraction():
    extraction = Extraction.create(DocumentID.new())
    extraction.pull_events()

    extraction.start()
    extraction.pull_events()

    extraction.complete()

    assert extraction.status.value == ExtractionStatus.EXTRACTED
    assert extraction.finished_at is not None

    events = extraction.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], ExtractionCompleted)


def test_cannot_complete_without_start():
    extraction = Extraction.create(DocumentID.new())

    with pytest.raises(InvalidOperation):
        extraction.complete()


def test_fail_extraction():
    extraction = Extraction.create(DocumentID.new())
    extraction.pull_events()

    extraction.start()
    extraction.pull_events()

    extraction.fail("OCR error")

    assert extraction.status.value == ExtractionStatus.FAILED
    assert extraction.error == "OCR error"

    events = extraction.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], ExtractionFailed)


def test_cannot_fail_if_not_running():
    extraction = Extraction.create(DocumentID.new())

    with pytest.raises(InvalidOperation):
        extraction.fail("boom")


def test_validate_extraction():
    extraction = Extraction.create(DocumentID.new())
    extraction.pull_events()

    extraction.start()
    extraction.pull_events()

    extraction.complete()
    extraction.pull_events()

    admin_id = UserID.new()
    extraction.validate(admin_id)

    assert extraction.status.value == ExtractionStatus.VALIDATED

    events = extraction.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], ExtractionValidated)
