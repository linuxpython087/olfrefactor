from django.db import models
from django_filters.rest_framework import DjangoFilterBackend
from processing.core.infrastructure.model_category_indicator import (
    Indicator,
    IndicatorCategory,
)
from processing.interfaces.filters import IndicatorFilter
from processing.interfaces.serializers import (
    IndicatorCategorySerializer,
    IndicatorSerializer,
)
from rest_framework import generics
from rest_framework.filters import OrderingFilter


class IndicatorListAPIView(generics.ListAPIView):
    """
    Liste des indicateurs (SVU)
    """

    queryset = Indicator.objects.select_related("category").filter(is_active=True)
    serializer_class = IndicatorSerializer

    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]

    filterset_class = IndicatorFilter

    ordering_fields = [
        "indicator_code",
        "label",
        "value_type",
    ]

    ordering = ["indicator_code"]


from django.db.models import Count
from rest_framework import generics


class IndicatorCategoryListAPIView(generics.ListAPIView):
    """
    Liste des catégories d’indicateurs
    """

    serializer_class = IndicatorCategorySerializer

    def get_queryset(self):
        return IndicatorCategory.objects.annotate(
            indicators_count=Count(
                "indicators", filter=models.Q(indicators__is_active=True)
            )
        ).order_by("label")
