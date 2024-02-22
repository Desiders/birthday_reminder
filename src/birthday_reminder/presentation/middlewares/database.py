from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from birthday_reminder.adapters.database import SQLAlchemyUoW
from birthday_reminder.adapters.database.repositories.birthday_remind import (
    BirthdayRemindReaderImpl,
    BirthdayRemindRepoImpl,
)
from birthday_reminder.adapters.database.repositories.user import (
    UserReaderImpl,
    UserRepoImpl,
)


class DatabaseMiddleware(BaseMiddleware):
    """
    This middleware is responsible for creating a new session for each request and passing it to the handler.
    It also creates and passes all repositories (and readers), `SQLAlchemyUoW` to the handler with the session.
    """

    def __init__(
        self,
        pool: async_sessionmaker[AsyncSession],
    ) -> None:
        self.pool = pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.pool() as session:
            # I think better to use DI framework here to pass the dependencies and not to create them here,
            # but right now it's not a big deal
            result = await handler(
                event,
                {
                    **data,
                    "uow": SQLAlchemyUoW(session),
                    "user_reader": UserReaderImpl(session),
                    "user_repo": UserRepoImpl(session),
                    "birthday_remind_reader": BirthdayRemindReaderImpl(
                        session
                    ),
                    "birthday_remind_repo": BirthdayRemindRepoImpl(session),
                },
            )

        return result
