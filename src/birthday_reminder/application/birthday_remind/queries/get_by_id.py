from uuid import UUID

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind


class GetByID(Interactor[UUID, BirthdayRemind]):
    def __init__(
        self,
        birthday_reader: BirthdayRemindReader,
        uow: UnitOfWork,
    ):
        self.birthday_reader = birthday_reader
        self.uow = uow

    async def __call__(self, id: UUID) -> BirthdayRemind:
        return await self.birthday_reader.get_by_id(id)
