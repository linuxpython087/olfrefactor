from django.db import models


class ExtractionDB(models.Model):
    id = models.CharField(max_length=36, primary_key=True)
    document_id = models.CharField(max_length=36, unique=True)

    status = models.CharField(max_length=20)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "extractions"
        indexes = [
            models.Index(fields=["document_id"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Extraction {self.id} ({self.status})"
