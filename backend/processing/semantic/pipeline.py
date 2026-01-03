# processing/semantic/pipeline.py

import logging

from processing.semantic.classifier import SemanticIndicatorClassifier
from processing.semantic.svu_vectorstore import get_svu_vectorstore

logger = logging.getLogger(__name__)


def classify_documents(docs):
    svu_store = get_svu_vectorstore()

    classifier = SemanticIndicatorClassifier(vectorstore=svu_store, batch_size=6)

    all_results = []

    for row in docs:
        all_results.extend(classifier.classify_row(row))

    return all_results
