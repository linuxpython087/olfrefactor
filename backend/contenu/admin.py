from contenu.core.infrastructure.model_region_pays import Country, Region
from contenu.core.infrastructure.models import DocumentDB
from django.contrib import admin


@admin.register(DocumentDB)
class DocumentDBAdmin(admin.ModelAdmin):
    list_display = ("id", "filename")
    list_filter = ("filename", "status")


# Register your models here.

admin.site.register(Region)
admin.site.register(Country)
