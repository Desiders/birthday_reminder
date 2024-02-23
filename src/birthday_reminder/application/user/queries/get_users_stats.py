from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.application.user import UserReader
from birthday_reminder.domain.user.entities import UsersStats


class GetUsersStats(Interactor[None, UsersStats]):
    def __init__(
        self,
        user_reader: UserReader,
        uow: UnitOfWork,
    ):
        self.user_reader = user_reader
        self.uow = uow

    async def __call__(self) -> UsersStats:
        return await self.user_reader.get_users_stats()
