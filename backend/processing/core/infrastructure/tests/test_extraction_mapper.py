import pytest
from processing.core.domaine.models import Extraction
from processing.core.infrastructure.mappers import ExtractionMapper
from processing.core.infrastructure.models import ExtractionDB
from shared.value_objects import DocumentID


@pytest.mark.django_db
class TestExtractionMapper:
    def test_domain_to_db_and_back(self):
        extraction = Extraction.create(DocumentID.new())
        extraction.start()
        extraction.complete()

        db = ExtractionMapper.to_db(extraction)
        db.save()

        domain = ExtractionMapper.to_domain(db)

        assert domain == extraction
