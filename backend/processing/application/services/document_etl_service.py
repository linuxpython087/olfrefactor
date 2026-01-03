import logging

from uploader_and_downloader.dropbox_storage import DropboxStorage

logger = logging.getLogger("etl.service")

import os

from processing.application.classification.classify_model import process_dataset_global
from processing.application.indexing.embeder_model import load_embedding_model
from processing.application.indexing.index_svu import index_svu
from processing.application.indexing.indicator_indexer import IndicatorIndexer
from processing.application.indexing.splitters import RawFactSplitter
from processing.application.indexing.vectore_store import (
    build_collection_name,
    create_vector_store_from_factchunks,
)
from processing.application.parsers.parser_factory import ParserFactory
from processing.application.retrieve.extract_indicator import direct_extraction
from processing.application.retrieve.retrieve_all_documents import dump_all_facts
from processing.application.services.cleaning.drop_null_rows import DropNullRowsCleaning
from processing.semantic.pipeline import classify_documents


class DocumentETLService:
    """
    Service applicatif ETL
    - Téléchargement réel
    - Étapes suivantes simulées pour l’instant
    """

    def __init__(self):
        self.storage = DropboxStorage()

    def process(self, document_id, document_url: str, filename) -> None:
        # ---------- DOWNLOAD ----------
        logger.info("⬇️ Téléchargement du document depuis Dropbox")
        content = self.storage.download(document_url)
        logger.info(f"📦 Fichier téléchargé ({len(content)} bytes)")
        index_svu()
        # indexer = IndicatorIndexer()
        # indexer.index_all()
        # ---------- PARSE  ----------
        logger.info("🧩 Parsing du document")

        parser = ParserFactory.from_document(
            document_id=document_id, content=content, filename=filename
        )

        parsed_data = parser.parse()
        # ---------- NORMALIZE (SIMULÉ) ----------
        logger.info("🧹 Parsing terminé")

        # ---------- splitter ----------
        logger.info("🧹 Debut du splitting")
        splitter = RawFactSplitter()

        chunks = splitter.split(parsed_data)
        # ---------- FIN----------
        logger.info("🧹 Fin du splitting")

        # ---------- Indexation ----------
        logger.info("🧹 Embedding")
        embeddings = load_embedding_model()

        logger.info("Création de collection")

        collection_name = build_collection_name(filename)
        logger.info("Debut d'indexation")
        store = create_vector_store_from_factchunks(
            chunks=chunks, embeddings=embeddings, collection_name=collection_name
        )

        logger.info("📊 Indexation terminée")
        retriev_docs = dump_all_facts(store, collection_name)
        # logger.info(f"Les 5 premiers documents recuperés: {retriev_docs[:5]}")

        # ---------- EXTRACT INDICATORS ----------
        logger.info("📊 Extraction des indicateurs")

        results = direct_extraction(docs=retriev_docs)
        logger.info(f"Les 5 premiers : {results[:5]}")

        # ---------- CLASSIFY par openapi ----------
        logger.info("🏷️ Classification des indicateurs")
        data_classified = classify_documents(docs=results)

        import json

        classified = json.dumps(data_classified, indent=2, ensure_ascii=False)
        logger.info(f"Les 5 premiers : {classified}")

        logger.info(f"🎯 Exemple sortie finale : {classified[:1]}")

        logger.info("🏷️ Classification des indicateurs decision final model local")
