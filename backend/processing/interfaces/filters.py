import django_filters
from django.db import models
from processing.core.infrastructure.model_category_indicator import Indicator


class IndicatorFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__code", lookup_expr="iexact"
    )

    value_type = django_filters.CharFilter(lookup_expr="iexact")

    is_active = django_filters.BooleanFilter()

    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(label__icontains=value)
            | models.Q(indicator_code__icontains=value)
            | models.Q(aliases__icontains=value)
            | models.Q(keywords__icontains=value)
        )

    class Meta:
        model = Indicator
        fields = ["category", "value_type", "is_active"]
