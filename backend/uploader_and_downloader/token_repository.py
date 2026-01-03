import time

from django.core.cache import cache


class DropboxTokenRepository:

    ACCESS_KEY = "dropbox:access_token"
    EXPIRY_KEY = "dropbox:access_token_expiry"

    def get_access_token(self) -> str | None:
        return cache.get(self.ACCESS_KEY)

    def save_access_token(self, token: str, expires_in: int):
        expiry_timestamp = int(time.time()) + expires_in - 60  # marge sécurité
        cache.set(self.ACCESS_KEY, token, timeout=expires_in)
        cache.set(self.EXPIRY_KEY, expiry_timestamp, timeout=expires_in)

    def is_token_valid(self) -> bool:
        expiry = cache.get(self.EXPIRY_KEY)
        return expiry and expiry > time.time()
