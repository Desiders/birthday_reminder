from uuid import UUID

from sqlalchemy import select

from birthday_reminder.adapters.database.converters import (
    model_to_user,
    user_to_model,
)
from birthday_reminder.application.user import UserReader, UserRepo
from birthday_reminder.domain.user.entities import User
from birthday_reminder.domain.user.exceptions import IDNotFound, TgIDNotFound

from ..exception_mapper import exception_mapper
from ..models import User as UserModel
from .base import Repo


class UserRepoImpl(Repo, UserRepo):
    @exception_mapper
    async def add(self, user: User) -> None:
        self._session.add(user_to_model(user))

        await self._session.flush()


class UserReaderImpl(Repo, UserReader):
    @exception_mapper
    async def get_by_id(self, id: UUID) -> User:
        user = await self._session.scalar(
            select(UserModel).filter(UserModel.id == id)
        )

        if user is None:
            raise IDNotFound(id)

        return model_to_user(user)

    @exception_mapper
    async def get_by_tg_id(self, tg_id: int) -> User:
        user = await self._session.scalar(
            select(UserModel).filter(UserModel.tg_id == tg_id)
        )

        if user is None:
            raise TgIDNotFound(tg_id)

        return model_to_user(user)
