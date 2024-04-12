from abc import abstractmethod
from typing import Protocol

from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
)


class Repo(Protocol):
    @abstractmethod
    async def add(
        self, completed_birthday_remind: CompletedBirthdayRemind
    ) -> None:
        raise NotImplementedError
