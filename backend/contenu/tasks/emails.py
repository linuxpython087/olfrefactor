import logging

from celery import shared_task

logger = logging.getLogger("celery.task.emails")


@shared_task(queue="emails")
def notify_admin_task(document_id: str, submitted_by: str):
    logger.info(
        "Admin notification sent",
        extra={
            "document_id": document_id,
            "submitted_by": submitted_by,
        },
    )


@shared_task(queue="emails")
def notify_admin_approval_task(document_id: str, approved_by: str):
    logger.info(
        "Document approved",
        extra={
            "document_id": document_id,
            "approved_by": approved_by,
        },
    )


@shared_task(queue="emails")
def notify_user_rejection_task(document_id: str, rejected_by: str, reason: str):
    logger.warning(
        "Document rejected",
        extra={
            "document_id": document_id,
            "rejected_by": rejected_by,
            "reason": reason,
        },
    )
