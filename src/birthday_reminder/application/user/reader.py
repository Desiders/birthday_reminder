from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from birthday_reminder.domain.user.entities import User


class Reader(Protocol):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_tg_id(self, tg_id: int) -> User:
        raise NotImplementedError
