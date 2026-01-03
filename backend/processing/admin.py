from django.contrib import admin
from processing.core.infrastructure.model_category_indicator import (
    Indicator,
    IndicatorCategory,
)

# Register your models here.
from processing.core.infrastructure.models import ExtractionDB

admin.site.register(ExtractionDB)
admin.site.register(IndicatorCategory)
admin.site.register(Indicator)
