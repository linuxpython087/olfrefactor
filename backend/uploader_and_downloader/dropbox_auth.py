import requests
from django.conf import settings
from uploader_and_downloader.token_repository import DropboxTokenRepository


class DropboxAuthService:

    TOKEN_URL = "https://api.dropboxapi.com/oauth2/token"

    def __init__(self):
        self.repo = DropboxTokenRepository()

    def get_valid_access_token(self) -> str:
        if self.repo.is_token_valid():
            return self.repo.get_access_token()

        return self.refresh_access_token()

    def refresh_access_token(self) -> str:
        response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": settings.DROPBOX_REFRESH_TOKEN,
                "client_id": settings.DROPBOX_APP_KEY,
                "client_secret": settings.DROPBOX_APP_SECRET,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        self.repo.save_access_token(
            token=data["access_token"], expires_in=data["expires_in"]
        )

        return data["access_token"]
