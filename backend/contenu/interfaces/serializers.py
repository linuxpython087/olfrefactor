# backend/contenu/core/api/serializers.py
from rest_framework import serializers


class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    source_type = serializers.CharField(max_length=50)


from contenu.core.domaine.model import Document
from rest_framework import serializers


class DocumentResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    filename = serializers.CharField()
    size = serializers.IntegerField()
    status = serializers.CharField()
    document_type = serializers.CharField(allow_null=True)
    url = serializers.URLField()

    def to_representation(self, doc: Document):
        return {
            "id": str(doc.id),
            "filename": doc.filename,
            "size": doc.size,
            "status": doc.status.value,
            "url": doc.storage_uri,
            "document_type": doc.document_type.value if doc.document_type else None,
        }


from contenu.core.infrastructure.model_region_pays import Country, Region
from rest_framework import serializers


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = [
            "id",
            "name",
            "continent",
        ]


class CountrySerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)

    class Meta:
        model = Country
        fields = [
            "id",
            "code_iso",
            "name",
            "region",
        ]
