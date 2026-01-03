from django.urls import path
from processing.interfaces.views import (
    IndicatorCategoryListAPIView,
    IndicatorListAPIView,
)

urlpatterns = [
    path("indicateurs/", IndicatorListAPIView.as_view(), name="indicator-list"),
    path(
        "categories/",
        IndicatorCategoryListAPIView.as_view(),
        name="indicator-category-list",
    ),
]
