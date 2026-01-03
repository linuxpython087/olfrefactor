from dataclasses import dataclass

from shared.exceptions import InvalidOperation


@dataclass(frozen=True)
class ExtractionStatus:
    value: str

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    EXTRACTED = "EXTRACTED"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"

    def __post_init__(self):
        if self.value not in {
            self.PENDING,
            self.RUNNING,
            self.EXTRACTED,
            self.VALIDATED,
            self.FAILED,
        }:
            raise InvalidOperation(f"Invalid ExtractionStatus: {self.value}")

    def can_start(self) -> bool:
        return self.value == self.PENDING

    def can_complete(self) -> bool:
        return self.value == self.RUNNING

    def can_validate(self) -> bool:
        return self.value == self.EXTRACTED

    def can_fail(self) -> bool:
        return self.value == self.RUNNING
