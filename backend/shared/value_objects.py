import uuid
from dataclasses import dataclass
from typing import Type, TypeVar

from shared.exceptions import InvalidOperation

T = TypeVar("T", bound="UUIDValueObject")


@dataclass(frozen=True)
class UUIDValueObject:
    value: uuid.UUID

    @classmethod
    def new(cls: Type[T]) -> T:
        return cls(uuid.uuid4())

    @classmethod
    def from_string(cls: Type[T], s: str) -> T:
        try:
            return cls(uuid.UUID(s))
        except ValueError:
            raise InvalidOperation(f"Invalid {cls.__name__}: {s}")

    def __str__(self) -> str:
        return str(self.value)

    def to_uuid(self) -> uuid.UUID:
        return self.value


class UserID(UUIDValueObject):
    pass


class TenantID(UUIDValueObject):
    pass


class DocumentID(UUIDValueObject):
    pass


class RoleID(UUIDValueObject):
    pass


class PermissionID(UUIDValueObject):
    pass


class ExtractionID(UUIDValueObject):
    pass
