from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
    ReminderType,
)


class Reader(Protocol):
    @abstractmethod
    async def get_by_birthday_remind_id_and_year_and_type(
        self,
        birthday_remind_id: UUID,
        year: int,
        type: ReminderType,
    ) -> CompletedBirthdayRemind:
        raise NotImplementedError
