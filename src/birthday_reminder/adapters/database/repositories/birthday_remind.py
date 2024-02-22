from uuid import UUID

from sqlalchemy import delete, select

from birthday_reminder.adapters.database.converters import (
    birthday_remind_to_model,
    model_to_birthday_remind,
)
from birthday_reminder.application.birthday_remind import (
    BirthdayRemindReader,
    BirthdayRemindRepo,
)
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind
from birthday_reminder.domain.birthday_remind.exceptions import IDNotFound

from ..exception_mapper import exception_mapper
from ..models import BirthdayRemind as BirthdayRemindModel
from .base import Repo


class BirthdayRemindRepoImpl(Repo, BirthdayRemindRepo):
    @exception_mapper
    async def add(self, birthday_remind: BirthdayRemind) -> None:
        self._session.add(birthday_remind_to_model(birthday_remind))

        await self._session.flush()

    @exception_mapper
    async def delete_by_id(self, id: UUID) -> None:
        await self._session.execute(
            delete(BirthdayRemindModel).filter(BirthdayRemindModel.id == id)
        )


class BirthdayRemindReaderImpl(Repo, BirthdayRemindReader):
    @exception_mapper
    async def get_by_id(self, id: UUID) -> BirthdayRemind:
        birthday_remind = await self._session.scalar(
            select(BirthdayRemindModel).filter(BirthdayRemindModel.id == id)
        )

        if birthday_remind is None:
            raise IDNotFound(id)

        return model_to_birthday_remind(birthday_remind)

    @exception_mapper
    async def get_by_user_id(self, user_id: UUID) -> list[BirthdayRemind]:
        birthday_reminds = await self._session.scalars(
            select(BirthdayRemindModel).filter(
                BirthdayRemindModel.user_id == user_id
            )
        )

        return [
            model_to_birthday_remind(birthday_remind)
            for birthday_remind in birthday_reminds
        ]
