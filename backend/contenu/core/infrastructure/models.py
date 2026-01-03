# backend/contenu/core/infrastructure/models.py
from django.contrib.auth import get_user_model
from django.db import models
from shared.enums import DocumentStatus, DocumentType

User = get_user_model()


class DocumentDB(models.Model):
    id = models.CharField(max_length=36, primary_key=True)  # UUID
    submitted_by = models.CharField(max_length=36)
    filename = models.CharField(max_length=255)
    size = models.BigIntegerField()
    source_type = models.CharField(max_length=50)

    storage_uri = models.URLField(null=True, blank=True)
    checksum = models.CharField(max_length=128, null=True, blank=True)

    status = models.CharField(max_length=50, default=DocumentStatus.DRAFT.value)

    document_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "documents"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{str(self.id)} {self.filename}"
