from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind


class Reader(Protocol):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> BirthdayRemind:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[BirthdayRemind]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id_and_sort_by_nearest(
        self, user_id: UUID, now_day: int, now_month: int
    ) -> list[BirthdayRemind]:
        raise NotImplementedError
