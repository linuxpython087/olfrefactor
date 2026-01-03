from uuid import uuid4

from domain.model import Document


class SubmitDocumentUseCase:
    def __init__(self, repo, storage, checksum_service, event_bus):
        self.repo = repo
        self.storage = storage
        self.checksum = checksum_service
        self.event_bus = event_bus

    def execute(self, *, tenant_id, user_id, file, source_type):
        document = Document(
            id=uuid4(),
            tenant_id=tenant_id,
            submitted_by=user_id,
            filename=file.name,
            size=file.size,
            source_type=source_type,
        )

        document.start_upload()
        self.repo.save(document)

        checksum = self.checksum.compute(file)
        uri = self.storage.upload(
            content=file,
            tenant_id=tenant_id,
            document_id=document.id,
            checksum=checksum,
        )

        document.mark_stored(uri, checksum)
        document.submit()
        self.repo.update(document)

        for event in document.pull_events():
            self.event_bus.publish(event)

        return {"document_id": document.id, "status": document.status}
