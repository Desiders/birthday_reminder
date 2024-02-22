from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.middlewares.user_context import EVENT_FROM_USER_KEY
from aiogram.types import TelegramObject, User

from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.application.user import UserReader
from birthday_reminder.application.user.queries import GetByTgID
from birthday_reminder.domain.user.exceptions import TgIDNotFound

logger = getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """
    This middleware is responsible for fetching the user from the database.
    If the user is not found, it will continue with the user as `None`.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data[EVENT_FROM_USER_KEY]
        if user is None:
            logger.debug("User is None")

            return await handler(event, data)

        user_reader: UserReader = data["user_reader"]
        uow: UnitOfWork = data["uow"]

        query = GetByTgID(user_reader, uow)

        try:
            db_user = await query(user.id)
        except TgIDNotFound as err:
            logger.warn(
                "User not found", extra={"tg_id": user.id, "error": err}
            )

            return await handler(event, data)

        return await handler(event, {**data, "db_user": db_user})
