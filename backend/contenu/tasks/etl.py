import logging

from celery import shared_task
from processing.application.commands.create_extraction import (
    CreateExtraction,
    FailExtraction,
    RunExtraction,
    StartExtraction,
)
from processing.application.commands.extraction_pipeline import ExtractionPipeline
from processing.core.domaine.repositories.django_extraction_repository import (
    DjangoExtractionRepository,
)

logger = logging.getLogger("celery.task.etl")


@shared_task(
    queue="etl_queue",
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
)
def run_etl_pipeline_task(document_id: str):
    logger.info(f"⚙️ ETL task lancée pour document {document_id}")

    repo = DjangoExtractionRepository()

    create_uc = CreateExtraction(repo)
    start_uc = StartExtraction(repo)
    run_uc = RunExtraction(repository=repo)  # logique ETL plus tard
    fail_uc = FailExtraction(repo, dispatcher=None)

    pipeline = ExtractionPipeline(
        create_uc=create_uc,
        start_uc=start_uc,
        run_uc=run_uc,
        fail_uc=fail_uc,
        repository=repo,
    )

    pipeline.run(document_id)

    logger.info(f"🏁 ETL terminé pour document {document_id}")
