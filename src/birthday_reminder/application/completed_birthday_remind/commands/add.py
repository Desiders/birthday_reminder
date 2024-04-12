from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.application.completed_birthday_remind import (
    CompletedBirthdayRemindRepo,
)
from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
)


class AddCompletedBirthdayRemind(Interactor[CompletedBirthdayRemind, None]):
    def __init__(
        self,
        completed_birthday_remind_repo: CompletedBirthdayRemindRepo,
        uow: UnitOfWork,
    ):
        self.completed_birthday_remind_repo = completed_birthday_remind_repo
        self.uow = uow

    async def __call__(
        self, completed_birthday_remind: CompletedBirthdayRemind
    ) -> None:
        await self.completed_birthday_remind_repo.add(
            completed_birthday_remind
        )
        await self.uow.commit()
