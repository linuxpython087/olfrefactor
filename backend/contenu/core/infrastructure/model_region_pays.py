from django.db import models


class Region(models.Model):
    name = models.CharField(max_length=100)
    continent = models.CharField(max_length=100)

    class Meta:
        unique_together = ("name", "continent")
        verbose_name = "Region"
        verbose_name_plural = "Regions"

    def __str__(self):
        return f"{self.name} ({self.continent})"


class Country(models.Model):
    code_iso = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=150)
    region = models.ForeignKey(
        Region, on_delete=models.PROTECT, related_name="countries"
    )

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.code_iso}]"
