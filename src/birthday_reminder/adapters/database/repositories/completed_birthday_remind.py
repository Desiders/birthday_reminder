from uuid import UUID

from sqlalchemy import select

from birthday_reminder.adapters.database.converters import (
    completed_birthday_remind_to_model,
    model_to_completed_birthday_remind,
)
from birthday_reminder.application.completed_birthday_remind import (
    CompletedBirthdayRemindReader,
    CompletedBirthdayRemindRepo,
)
from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
    ReminderType,
)
from birthday_reminder.domain.completed_birthday_remind.exceptions import (
    IDForYearAndTypeNotFound,
)

from ..exception_mapper import exception_mapper
from ..models import CompletedBirthdayRemind as CompletedBirthdayRemindModel
from .base import Repo


class CompletedBirthdayRemindRepoImpl(Repo, CompletedBirthdayRemindRepo):
    @exception_mapper
    async def add(
        self, completed_birthday_remind: CompletedBirthdayRemind
    ) -> None:
        self._session.add(
            completed_birthday_remind_to_model(completed_birthday_remind)
        )

        await self._session.flush()


class CompletedBirthdayRemindReaderImpl(Repo, CompletedBirthdayRemindReader):
    @exception_mapper
    async def get_by_birthday_remind_id_and_year_and_type(
        self,
        birthday_remind_id: UUID,
        year: int,
        type: ReminderType,
    ) -> CompletedBirthdayRemind:
        birthday_remind = await self._session.scalar(
            select(CompletedBirthdayRemindModel).filter(
                CompletedBirthdayRemindModel.birthday_remind_id
                == birthday_remind_id,
                CompletedBirthdayRemindModel.year == year,
                CompletedBirthdayRemindModel.reminder_type == type,
            )
        )

        if birthday_remind is None:
            raise IDForYearAndTypeNotFound(birthday_remind_id, year, type)

        return model_to_completed_birthday_remind(birthday_remind)
