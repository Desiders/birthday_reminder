from logging import getLogger

from aiogram import Bot
from aiogram.types import Update, User

from birthday_reminder.domain.user.entities import User as UserDB

logger = getLogger(__name__)


async def is_new_user(
    update: Update,
    bot: Bot,
    db_user: UserDB | None = None,
    user: User | None = None,
) -> bool:
    if user is None:
        logger.error("User is None")

        return False

    result = db_user is None

    if result:
        logger.debug("New user", extra={"tg_user_id": user.id})
    else:
        logger.debug(
            "User already exists",
            extra={"tg_user_id": user.id},
        )

    return result
