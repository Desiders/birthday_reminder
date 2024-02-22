from birthday_reminder.application.common import Interactor, UnitOfWork
from birthday_reminder.application.user import UserReader
from birthday_reminder.domain.user.entities import User


class GetByTgID(Interactor[int, User]):
    def __init__(
        self,
        user_reader: UserReader,
        uow: UnitOfWork,
    ):
        self.user_reader = user_reader
        self.uow = uow

    async def __call__(self, tg_id: int) -> User:
        return await self.user_reader.get_by_tg_id(tg_id)
