from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import (
    BirthdayRemindersStats,
)


class GetBirthdayRemindersStats(Interactor[None, BirthdayRemindersStats]):
    def __init__(
        self,
        birthday_remind_reader: BirthdayRemindReader,
        uow: UnitOfWork,
    ):
        self.birthday_remind_reader = birthday_remind_reader
        self.uow = uow

    async def __call__(self) -> BirthdayRemindersStats:
        return await self.birthday_remind_reader.get_birthday_reminders_stats()
