from uuid import UUID

from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.application.completed_birthday_remind import (
    CompletedBirthdayRemindReader,
)
from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
    ReminderType,
)


class GetByBirthdayRemindIDAndYear(Interactor[int, CompletedBirthdayRemind]):
    def __init__(
        self,
        completed_birthday_reader: CompletedBirthdayRemindReader,
        uow: UnitOfWork,
    ):
        self.completed_birthday_reader = completed_birthday_reader
        self.uow = uow

    async def __call__(
        self,
        birthday_remind_id: UUID,
        year: int,
        type: ReminderType,
    ) -> CompletedBirthdayRemind:
        return await self.completed_birthday_reader.get_by_birthday_remind_id_and_year_and_type(
            birthday_remind_id, year, type
        )
