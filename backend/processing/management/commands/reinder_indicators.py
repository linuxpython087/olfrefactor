from django.core.management.base import BaseCommand
from processing.application.indexing.indicator_indexer import IndicatorIndexer


class Command(BaseCommand):
    help = "Rebuild Qdrant index from SVU indicators"

    def handle(self, *args, **options):
        indexer = IndicatorIndexer()
        indexer.index_all()
        self.stdout.write(self.style.SUCCESS("✔ Indicator semantic index rebuilt"))
