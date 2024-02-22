from dataclasses import dataclass
from uuid import UUID

from birthday_reminder.domain.common.exceptions import DomainException


@dataclass(eq=False)
class IDNotFound(DomainException):
    id: UUID

    @property
    def title(self) -> str:
        return f"A birthday remind with id {self.id} not found"
