from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind


class Repo(Protocol):
    @abstractmethod
    async def add(self, birthday_remind: BirthdayRemind) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> None:
        raise NotImplementedError
