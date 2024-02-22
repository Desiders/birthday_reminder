from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.application.user import UserRepo
from birthday_reminder.domain.user.entities import User


class AddUser(Interactor[User, None]):
    def __init__(
        self,
        user_repo: UserRepo,
        uow: UnitOfWork,
    ):
        self.user_repo = user_repo
        self.uow = uow

    async def __call__(self, user: User) -> None:
        await self.user_repo.add(user)
        await self.uow.commit()
