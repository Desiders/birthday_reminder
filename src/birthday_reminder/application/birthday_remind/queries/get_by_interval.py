from dataclasses import dataclass

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind


@dataclass
class GetByIntervalRequest:
    start_day: int
    start_month: int
    end_day: int
    end_month: int


class GetByInterval(Interactor[GetByIntervalRequest, list[BirthdayRemind]]):
    def __init__(
        self,
        birthday_reader: BirthdayRemindReader,
        uow: UnitOfWork,
    ):
        self.birthday_reader = birthday_reader
        self.uow = uow

    async def __call__(
        self, dto: GetByIntervalRequest
    ) -> list[BirthdayRemind]:
        return await self.birthday_reader.get_by_interval(
            dto.start_day,
            dto.start_month,
            dto.end_day,
            dto.end_month,
        )
