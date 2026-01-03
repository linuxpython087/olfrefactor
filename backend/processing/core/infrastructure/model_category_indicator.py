# processing/core/infrastructure/models.py

from django.db import models


class IndicatorCategory(models.Model):
    """
    Catégories métier des indicateurs
    """

    code = models.CharField(max_length=100, unique=True, db_index=True)
    label = models.CharField(max_length=255)

    class Meta:
        db_table = "Category des indicateurs"

    def __str__(self):
        return self.label


class Indicator(models.Model):
    """
    Source de Vérité Unique – Indicateur
    """

    indicator_id = models.CharField(max_length=50, unique=True, db_index=True)

    indicator_code = models.CharField(max_length=255, unique=True, db_index=True)

    label = models.CharField(max_length=512)

    description = models.TextField(null=True, blank=True)

    category = models.ForeignKey(
        IndicatorCategory, on_delete=models.PROTECT, related_name="indicators"
    )

    value_type = models.CharField(max_length=50, null=True, blank=True)

    unit = models.CharField(max_length=50, null=True, blank=True)

    keywords = models.JSONField(default=list, blank=True)

    aliases = models.JSONField(default=list, blank=True)

    validation_rules = models.JSONField(null=True, blank=True)

    source = models.JSONField(default=list, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "indicateurs"
        indexes = [
            models.Index(fields=["indicator_code"]),
            models.Index(fields=["indicator_id"]),
        ]

    def __str__(self):
        return self.indicator_code
