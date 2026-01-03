import pytest
from processing.core.domaine.models import Extraction
from processing.core.domaine.repositories.django_extraction_repository import (
    DjangoExtractionRepository,
)
from shared.value_objects import DocumentID


@pytest.mark.django_db
def test_save_and_get_extraction():
    repo = DjangoExtractionRepository()

    extraction = Extraction.create(DocumentID.new())
    extraction.start()
    extraction.complete()

    repo.save(extraction)

    loaded = repo.get_by_id(extraction.id)

    assert loaded is not None
    assert loaded.id == extraction.id
    assert loaded.status.value == extraction.status.value
