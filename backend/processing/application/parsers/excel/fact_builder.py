import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class RawFact:
    entity_type: str  # ex: "raw_row"
    entity_id: str  # hash stable
    source: Dict[str, Any]  # file, sheet, row_index
    payload: Dict[str, Any]  # row COMPLETE
    provenance: Dict[str, Any]


class BlindFactBuilder:
    ENTITY_TYPE = "raw_row"

    def build(self, row: dict, source: dict, row_index: int) -> RawFact:
        payload = row.copy()

        # hash stable = identité du chunk
        raw_id = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()

        return RawFact(
            entity_type=self.ENTITY_TYPE,
            entity_id=raw_id,
            source={**source, "row": row_index},
            payload=payload,
            provenance={"pipeline": "raw_ingestion", "version": "v1"},
        )
