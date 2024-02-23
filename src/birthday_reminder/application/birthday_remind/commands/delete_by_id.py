from uuid import UUID

from birthday_reminder.application.birthday_remind import BirthdayRemindRepo
from birthday_reminder.application.common import Interactor, UnitOfWork


class DeleteBirthdayRemindById(Interactor[UUID, None]):
    def __init__(
        self,
        birthday_remind_repo: BirthdayRemindRepo,
        uow: UnitOfWork,
    ):
        self.birthday_remind_repo = birthday_remind_repo
        self.uow = uow

    async def __call__(self, id: UUID) -> None:
        await self.birthday_remind_repo.delete_by_id(id)
        await self.uow.commit()
