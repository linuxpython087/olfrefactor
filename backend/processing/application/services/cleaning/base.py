from abc import ABC, abstractmethod
from typing import Any, Dict, List


class DataCleaningStrategy(ABC):
    @abstractmethod
    def clean(
        self, parsed_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        ...
