# processing/semantic/classifier.py

from typing import Any, Dict, List

from processing.semantic.embeddings import EmbeddingService
from processing.semantic.normalization import extract_semantic_fields


class SemanticIndicatorClassifier:
    def __init__(self, vectorstore, batch_size: int = 16):
        self.vectorstore = vectorstore
        self.batch_size = batch_size
        self.embeddings = EmbeddingService()

    def _batch(self, items: List[str]):
        for i in range(0, len(items), self.batch_size):
            yield items[i : i + self.batch_size]

    def classify_row(self, row: Dict[str, Any]) -> List[Dict[str, Any]]:
        semantic_fields = extract_semantic_fields(row)
        if not semantic_fields:
            return []

        field_names = list(semantic_fields.keys())
        results: List[Dict[str, Any]] = []

        for batch in self._batch(field_names):
            vectors = self.embeddings.embed_many(batch)

            for field, vector in zip(batch, vectors):
                # ✅ LA BONNE MÉTHODE
                matches = self.vectorstore.similarity_search_with_score_by_vector(
                    vector, k=3
                )

                results.append(
                    {
                        "raw_field": field,
                        "raw_value": semantic_fields[field],
                        "candidates": [
                            {
                                "indicator_id": doc.metadata.get("indicator_id"),
                                "indicator_code": doc.metadata.get("indicator_code"),
                                "category": doc.metadata.get("category_code"),
                                "unit": doc.metadata.get("unit"),
                                "score": round(score, 3),  # ✅ score réel
                            }
                            for doc, score in matches
                        ],
                    }
                )

        return results
