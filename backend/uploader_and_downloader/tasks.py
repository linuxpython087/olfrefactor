from celery import shared_task
from uploader_and_downloader.dropbox_auth import DropboxAuthService


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def refresh_dropbox_token_task(self):
    DropboxAuthService().refresh_access_token()
