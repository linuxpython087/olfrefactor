from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class FactChunk:
    id: str
    text: str
    payload: Dict[str, Any]


import json


class RawFactSplitter:
    """
    Splitter universel :
    - 1 RawFact = 1 chunk
    - ZÉRO logique métier
    - AUCUNE perte de données
    """

    def split(self, raw_facts: list) -> list:
        chunks = []

        for rf in raw_facts:
            chunks.append(
                FactChunk(
                    id=rf.entity_id,
                    text=self._to_text(rf),
                    payload=self._to_payload(rf),
                )
            )

        return chunks

        # -------------------------
        # PAYLOAD = RAWFACT COMPLET
        # -------------------------

    def _to_payload(self, rf) -> dict:
        return {
            "entity_type": rf.entity_type,
            "source": rf.source,
            "payload": rf.payload,
            "provenance": rf.provenance,
        }

    # -------------------------
    # TEXT = SÉRIALISATION GÉNÉRIQUE
    # -------------------------
    def _to_text(self, rf) -> str:
        """
        Représentation textuelle neutre, stable, exhaustive.
        Sert UNIQUEMENT à l'embedding.
        """
        return json.dumps(
            {"entity_type": rf.entity_type, "source": rf.source, "data": rf.payload},
            ensure_ascii=False,
            sort_keys=True,
        )
