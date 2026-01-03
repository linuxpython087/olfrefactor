import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from processing.core.infrastructure.model_category_indicator import (
    Indicator,
    IndicatorCategory,
)


class Command(BaseCommand):
    help = "Import indicators from SVU JSON"

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str)

    def handle(self, *args, **options):
        path = options["json_path"]

        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        indicators = payload["indicators"]

        for item in indicators:
            category_code = item["category"]

            category, _ = IndicatorCategory.objects.get_or_create(
                code=category_code,
                defaults={"label": category_code.replace("_", " ").title()},
            )

            try:
                with transaction.atomic():
                    Indicator.objects.update_or_create(
                        indicator_id=item["indicator_id"],
                        defaults={
                            "indicator_code": item["indicator_code"],
                            "label": item["label"],
                            "description": item.get("description"),
                            "category": category,
                            "value_type": item.get("value_type"),
                            "unit": item.get("unit"),
                            "keywords": item.get("keywords", []),
                            "aliases": item.get("aliases", []),
                            "validation_rules": item.get("validation_rules"),
                            "source": item.get("source", []),
                            "is_active": True,
                        },
                    )

            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠ Duplicate indicator_code skipped: {item['indicator_code']} "
                        f"(indicator_id={item['indicator_id']})"
                    )
                )

        self.stdout.write(self.style.SUCCESS("✔ Indicators import completed"))
