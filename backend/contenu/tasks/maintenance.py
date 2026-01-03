from celery import shared_task


@shared_task(queue="maintenance")
def escalate_to_sysadmin_task(document_id: str, submitted_by: str):
    print(f"🚀 Upload started | doc={document_id} by={submitted_by}")
