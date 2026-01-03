from abc import ABC, abstractmethod


class IDocumentStorage(ABC):
    """Interface générique pour stocker les documents dans le cloud."""

    @abstractmethod
    def upload(self, content: bytes, filename: str) -> str:
        """
        Upload un fichier dans le cloud.
        Args:
            content: bytes du fichier
            filename: nom du fichier
        Returns:
            str: URL publique ou signée pour accéder au fichier
        """
        pass

    @abstractmethod
    def download(self, url: str) -> bytes:
        """
        Télécharger un fichier depuis le cloud.
        Args:
            url: URL du fichier
        Returns:
            bytes du fichier
        """
        pass

    @abstractmethod
    def delete(self, url: str) -> None:
        """
        Supprimer un fichier depuis le cloud.
        Args:
            url: URL du fichier à supprimer
        """
        pass
