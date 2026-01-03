import logging

from celery import shared_task

logger = logging.getLogger("celery.task.document")


@shared_task(queue="documents")
def log_upload_started_task(document_id: str, submitted_by: str):
    logger.info(f"🚀 Upload started | doc={document_id} by={submitted_by}")
