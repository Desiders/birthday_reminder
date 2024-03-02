import asyncio
from asyncio import Queue
from datetime import date
from logging import getLogger

from aiogram import Bot
from aiogram.exceptions import (
    RestartingTelegram,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramNotFound,
    TelegramRetryAfter,
    TelegramServerError,
)

from birthday_reminder.application.common.exceptions import RepoError
from birthday_reminder.application.user.queries import GetByID
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind
from birthday_reminder.domain.user.exceptions import IDNotFound

logger = getLogger(__name__)


async def send_message_with_retries(
    bot: Bot,
    user_id: int,
    text: str,
    parse_mode: str | None = None,
) -> None:
    while True:
        try:
            await bot.send_message(
                user_id,
                text,
                parse_mode=parse_mode,
                disable_web_page_preview=True,
                disable_notification=False,
            )

            break
        except TelegramRetryAfter as err:
            logger.warn(
                "TelegramRetryAfter",
                extra={"retry_after": err.retry_after},
            )

            await asyncio.sleep(err.retry_after)
        except TelegramNetworkError as err:
            logger.error("TelegramNetworkError", exc_info=err)

            await asyncio.sleep(5)
        except (TelegramNotFound, TelegramForbiddenError) as err:
            logger.error(
                "TelegramNotFound or TelegramForbiddenError", exc_info=err
            )

            break
        except (TelegramServerError, RestartingTelegram) as err:
            logger.error(
                "TelegramServerError or RestartingTelegram", exc_info=err
            )

            await asyncio.sleep(5)
        except Exception as err:
            logger.error("Unknown error", exc_info=err)

            break


async def consumer(
    queue: Queue[BirthdayRemind],
    query: GetByID,
    bot: Bot,
) -> None:
    logger.debug("Starting the consumer")

    while True:
        birthday_remind = await queue.get()

        logger.info(f"Consumed: {birthday_remind}")

        try:
            user = await query(birthday_remind.user_id)
        except IDNotFound as err:
            logger.warn(err)

            continue
        except RepoError as err:
            logger.error("Error while getting user by ID", exc_info=err)

            continue

        today = date.today()

        today_day = today.day
        today_month = today.month

        if (
            today_day == birthday_remind.day
            and today_month == birthday_remind.month
        ):
            logger.debug(
                "Today is birthday",
                extra={"birthday_remind": birthday_remind},
            )

            text = f"Today is {birthday_remind.name}'s birthday! 🎉"
        else:
            logger.debug(
                "Birthday is coming soon",
                extra={"birthday_remind": birthday_remind},
            )

            text = f"Your friend {birthday_remind.name}'s birthday is coming soon! 🎉"

        await send_message_with_retries(
            bot,
            user.tg_id,
            text,
            parse_mode=None,
        )

        queue.task_done()

        await asyncio.sleep(0.03)
