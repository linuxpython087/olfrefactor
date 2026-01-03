from processing.core.infrastructure.model_category_indicator import (
    Indicator,
    IndicatorCategory,
)
from rest_framework import serializers


class IndicatorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicatorCategory
        fields = ["code", "label"]


class IndicatorSerializer(serializers.ModelSerializer):
    category = IndicatorCategorySerializer(read_only=True)

    id = serializers.CharField(source="indicator_id", read_only=True)

    code = serializers.CharField(source="indicator_code", read_only=True)

    class Meta:
        model = Indicator
        fields = [
            "id",
            "code",
            "label",
            "description",
            "category",
            "value_type",
            "unit",
            "aliases",
            "keywords",
            "is_active",
        ]
