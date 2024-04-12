from dataclasses import dataclass
from uuid import UUID

from birthday_reminder.domain.common.exceptions import DomainException
from birthday_reminder.domain.completed_birthday_remind.entities import (
    ReminderType,
)


@dataclass(eq=False)
class IDForYearAndTypeNotFound(DomainException):
    birthday_remind_id: UUID
    year: int
    type: ReminderType

    @property
    def title(self) -> str:
        return f"A completed birthday remind with the birthday remind ID {self.birthday_remind_id}, year {self.year}, and type {self.type} was not found."
