from celery import shared_task
from processing.application.indexing.indicator_indexer import IndicatorIndexer


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 30},
    retry_backoff=True,
)
def reindex_indicators_task(self):
    """
    Rebuild / sync SVU indicators into Qdrant
    """
    indexer = IndicatorIndexer()
    indexer.index_all()
    return "SVU indicators indexed"
