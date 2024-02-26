from abc import abstractmethod
from typing import Protocol

from birthday_reminder.domain.user.entities import User


class Repo(Protocol):
    @abstractmethod
    async def add(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> None:
        raise NotImplementedError
