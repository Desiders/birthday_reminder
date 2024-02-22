from dataclasses import dataclass
from uuid import UUID

from birthday_reminder.domain.common.exceptions import DomainException


@dataclass(eq=False)
class IDNotFound(DomainException):
    id: UUID

    @property
    def title(self) -> str:
        return f"A user with ID {self.id} not found"


@dataclass(eq=False)
class TgIDNotFound(DomainException):
    tg_id: int

    @property
    def title(self) -> str:
        return f"A user with Telegram ID {self.tg_id} not found"
