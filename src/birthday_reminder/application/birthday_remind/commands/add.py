from birthday_reminder.application.birthday_remind import BirthdayRemindRepo
from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind


class AddBirthdayRemind(Interactor[BirthdayRemind, None]):
    def __init__(
        self,
        birthday_remind_repo: BirthdayRemindRepo,
        uow: UnitOfWork,
    ):
        self.birthday_remind_repo = birthday_remind_repo
        self.uow = uow

    async def __call__(self, birthday_remind: BirthdayRemind) -> None:
        await self.birthday_remind_repo.add(birthday_remind)
        await self.uow.commit()
