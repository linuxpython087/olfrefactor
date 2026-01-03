# backend/contenu/core/api/urls.py
from contenu.interfaces.views import (
    ApproveDocumentView,
    CountryListAPIView,
    RegionListAPIView,
    RejectDocumentView,
    RequestDeleteDocumentView,
    RequestUpdateDocumentView,
    SubmitDocumentView,
)
from django.urls import path

urlpatterns = [
    path("documents/submit/", SubmitDocumentView.as_view(), name="submit-document"),
    path(
        "documents/<uuid:doc_id>/approve/",
        ApproveDocumentView.as_view(),
        name="approve_document",
    ),
    path(
        "documents/<uuid:doc_id>/reject/",
        RejectDocumentView.as_view(),
        name="reject_document",
    ),
    path(
        "documents/<uuid:doc_id>/request-update/",
        RequestUpdateDocumentView.as_view(),
        name="request_update_document",
    ),
    path(
        "documents/<uuid:doc_id>/request-delete/",
        RequestDeleteDocumentView.as_view(),
        name="request_delete_document",
    ),
    path("regions/", RegionListAPIView.as_view(), name="region-list"),
    path("pays-olf/", CountryListAPIView.as_view(), name="country-list"),
]
