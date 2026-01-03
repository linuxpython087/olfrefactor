# backend/contenu/core/api/views.py
from contenu.application.dependancy_injection import (
    build_document_actions_service,
    build_document_service,
)
from contenu.core.domaine.model import Document
from contenu.interfaces.serializers import (
    DocumentResponseSerializer,
    DocumentUploadSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.value_objects import DocumentID, UserID


class SubmitDocumentView(APIView):
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        source_type = serializer.validated_data["source_type"]

        user_id = UserID.from_string(str("c618610f-41d5-49cd-a8ac-b405acdf84d1"))

        doc = Document(
            id=DocumentID.new(),
            submitted_by=user_id,
            filename=file.name,
            size=file.size,
            source_type=source_type,
        )

        service = build_document_service()
        doc = service.submit_document(doc, file)

        serializer = DocumentResponseSerializer()

        return Response(
            serializer.to_representation(doc), status=status.HTTP_201_CREATED
        )

        # return Response({
        #     "document_id": str(doc.id),
        #     "status": doc.status.value,
        #     "filename": doc.filename,
        #     'url': doc.storage_uri,
        # }, status=status.HTTP_201_CREATED)


from rest_framework.exceptions import APIException, NotFound, ValidationError
from shared.value_objects import InvalidOperation


class ApproveDocumentView(APIView):
    def post(self, request, doc_id):
        admin_id = UserID.from_string(str("c618610f-41d5-49cd-a8ac-b405acdf84d1"))
        service = build_document_actions_service()
        try:
            doc = service.approve(doc_id, admin_id)
            return Response(
                {"document_id": str(doc.id), "status": doc.status},
                status=status.HTTP_200_OK,
            )
        except InvalidOperation as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:  # document not found
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RejectDocumentView(APIView):
    def post(self, request, doc_id):
        admin_id = UserID.from_string(str("c618610f-41d5-49cd-a8ac-b405acdf84d1"))
        reason = request.data.get("reason", "")
        try:
            service = build_document_actions_service()
            doc = service.reject(doc_id, admin_id, reason)
            return Response(
                {"document_id": str(doc.id), "status": doc.status},
                status=status.HTTP_200_OK,
            )
        except InvalidOperation as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:  # document not found
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RequestUpdateDocumentView(APIView):
    def post(self, request, doc_id):
        user_id = UserID.from_string(str("c618610f-41d5-49cd-a8ac-b405acdf84d1"))
        try:
            service = build_document_actions_service()
            doc = service.request_update(doc_id, user_id)
            return Response(
                {"document_id": str(doc.id), "status": doc.status},
                status=status.HTTP_200_OK,
            )
        except:
            return Response(
                {"document_id": str(doc.id), "status": doc.status},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RequestDeleteDocumentView(APIView):
    def post(self, request, doc_id):
        user_id = UserID.from_string(str("c618610f-41d5-49cd-a8ac-b405acdf84d1"))
        service = build_document_actions_service()
        doc = service.request_delete(doc_id, user_id)
        return Response(
            {"document_id": str(doc.id), "status": doc.status},
            status=status.HTTP_200_OK,
        )


# region pay

from contenu.core.infrastructure.model_region_pays import Country, Region
from contenu.interfaces.serializers import CountrySerializer, RegionSerializer
from django.db.models import Q
from rest_framework.generics import ListAPIView


class RegionListAPIView(ListAPIView):
    serializer_class = RegionSerializer

    def get_queryset(self):
        queryset = Region.objects.all().order_by("continent", "name")

        continent = self.request.query_params.get("continent")
        if continent:
            queryset = queryset.filter(continent__iexact=continent)

        return queryset


class CountryListAPIView(ListAPIView):
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.select_related("region").all().order_by("name")

        region_id = self.request.query_params.get("region_id")
        continent = self.request.query_params.get("continent")
        code_iso = self.request.query_params.get("code_iso")

        if region_id:
            queryset = queryset.filter(region_id=region_id)

        if continent:
            queryset = queryset.filter(region__continent__iexact=continent)

        if code_iso:
            queryset = queryset.filter(code_iso__iexact=code_iso)

        return queryset
