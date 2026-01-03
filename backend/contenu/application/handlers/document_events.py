def on_document_delete_requested(event, repo, storage):
    document = repo.get(event.document_id)
    if document and document.storage_uri:
        storage.delete(storage_uri=document.storage_uri)
    repo.delete(event.document_id)


def on_document_ready_for_etl(event):
    start_etl_pipeline.delay(str(event.document_id))
