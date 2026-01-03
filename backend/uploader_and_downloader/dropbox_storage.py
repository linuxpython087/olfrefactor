# uploader_and_downloader/dropbox_storage.py

import re
from typing import IO, Union
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import dropbox
import requests
from dropbox.exceptions import ApiError, AuthError
from dropbox.sharing import RequestedVisibility, SharedLinkSettings
from uploader_and_downloader.base import IDocumentStorage

from .dropbox_auth import DropboxAuthService

CHUNK_SIZE = 4 * 1024 * 1024


class DropboxStorage(IDocumentStorage):
    """
    Implémentation robuste de IDocumentStorage pour Dropbox
    avec refresh automatique du token expiré.
    """

    def __init__(self):
        self.auth_service = DropboxAuthService()
        self._refresh_client()

    def _refresh_client(self):
        token = self.auth_service.get_valid_access_token()
        self.client = dropbox.Dropbox(token)

    # ==========================
    # Utils
    # ==========================

    def _force_direct_download(self, url: str) -> str:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        query["dl"] = ["1"]
        return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))

    def _retry_on_auth_error(self, func, *args, **kwargs):
        """
        Exécute une action Dropbox.
        Si AuthError → refresh token → retry une fois.
        """
        try:
            return func(*args, **kwargs)
        except AuthError:
            self._refresh_client()
            return func(*args, **kwargs)

    # ==========================
    # Dropbox API
    # ==========================

    def _get_or_create_shared_link(self, path: str) -> str:
        try:
            link = self._retry_on_auth_error(
                self.client.sharing_create_shared_link_with_settings,
                path,
                SharedLinkSettings(requested_visibility=RequestedVisibility.public),
            ).url

        except ApiError as e:
            if e.error.is_shared_link_already_exists():
                links = self._retry_on_auth_error(
                    self.client.sharing_list_shared_links, path=path
                ).links

                if not links:
                    raise RuntimeError("Lien partagé censé exister mais introuvable")
                link = links[0].url
            else:
                raise

        return self._force_direct_download(link)

    def download(self, url: str) -> bytes:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.content

    def delete(self, url: str) -> None:
        try:
            metadata = self._retry_on_auth_error(
                self.client.sharing_get_shared_link_metadata, url
            )

            if not hasattr(metadata, "path_lower"):
                raise RuntimeError("Impossible de résoudre le chemin Dropbox")

            self._retry_on_auth_error(self.client.files_delete_v2, metadata.path_lower)

        except ApiError as e:
            if e.error.is_path_lookup() and e.error.get_path_lookup().is_not_found():
                # idempotent delete
                return
            raise

    def _upload_stream(self, content: IO[bytes], path: str):
        first_chunk = content.read(CHUNK_SIZE)
        if not first_chunk:
            raise ValueError("Fichier vide")

        start = self._retry_on_auth_error(
            self.client.files_upload_session_start, first_chunk
        )

        offset = len(first_chunk)

        cursor = dropbox.files.UploadSessionCursor(
            session_id=start.session_id, offset=offset
        )

        while True:
            chunk = content.read(CHUNK_SIZE)
            if not chunk:
                break

            self._retry_on_auth_error(
                self.client.files_upload_session_append_v2, chunk, cursor
            )

            cursor.offset += len(chunk)

        self._retry_on_auth_error(
            self.client.files_upload_session_finish,
            b"",
            cursor,
            dropbox.files.CommitInfo(path=path),
        )

    def upload(
        self,
        content: Union[bytes, IO[bytes]],
        filename: str,
        submitted_by: str,
        document_id: str,
    ) -> str:
        path = f"/tenants/{submitted_by}/documents/{document_id}/{filename}"

        if isinstance(content, bytes):
            self._retry_on_auth_error(
                self.client.files_upload,
                content,
                path,
                mode=dropbox.files.WriteMode.overwrite,
            )
        else:
            self._upload_stream(content, path)

        return self._get_or_create_shared_link(path)
