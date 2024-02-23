from dataclasses import dataclass
from uuid import UUID

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind


@dataclass
class GetByUserIDAndSortByNearestRequest:
    user_id: UUID
    now_day: int
    now_month: int


class GetByUserIDAndSortByNearest(
    Interactor[GetByUserIDAndSortByNearestRequest, list[BirthdayRemind]]
):
    def __init__(
        self,
        birthday_reader: BirthdayRemindReader,
        uow: UnitOfWork,
    ):
        self.birthday_reader = birthday_reader
        self.uow = uow

    async def __call__(
        self, dto: GetByUserIDAndSortByNearestRequest
    ) -> list[BirthdayRemind]:
        return await self.birthday_reader.get_by_user_id_and_sort_by_nearest(
            dto.user_id, dto.now_day, dto.now_month
        )
