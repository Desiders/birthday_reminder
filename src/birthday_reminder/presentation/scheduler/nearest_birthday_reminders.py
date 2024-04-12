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
from fluent.runtime import FluentLocalization
from uuid6 import uuid7

from birthday_reminder.application.common.exceptions import RepoError
from birthday_reminder.application.completed_birthday_remind.commands import (
    AddCompletedBirthdayRemind,
)
from birthday_reminder.application.completed_birthday_remind.queries import (
    GetByBirthdayRemindIDAndYear,
)
from birthday_reminder.application.user.queries import GetByID
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind
from birthday_reminder.domain.completed_birthday_remind.entities import (
    CompletedBirthdayRemind,
    ReminderType,
)
from birthday_reminder.domain.completed_birthday_remind.exceptions import (
    IDForYearAndTypeNotFound,
)
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
    get_by_id: GetByID,
    get_completed_birthday_remind: GetByBirthdayRemindIDAndYear,
    add_completed_birthday_remind: AddCompletedBirthdayRemind,
    bot: Bot,
    l10ns: dict[str, FluentLocalization],
    default_lang: str,
) -> None:
    logger.debug("Starting the consumer")

    while True:
        remind = await queue.get()

        logger.info(f"Consumed: {remind}")

        try:
            user = await get_by_id(remind.user_id)
        except IDNotFound as err:
            logger.warn(err)

            continue
        except RepoError as err:
            logger.error("Error while getting user by ID", exc_info=err)

            await asyncio.sleep(5)

            continue
        except Exception as err:
            logger.critical(
                "Unknown error while getting user by ID", exc_info=err
            )

            await asyncio.sleep(5)

            continue

        today = date.today()

        today_day = today.day
        today_month = today.month

        lang = user.language_code

        if not lang:
            lang = default_lang
        elif lang not in l10ns:
            lang = default_lang

            logger.debug(
                "Language not found, using default", extra={"lang": lang}
            )

        l10n = l10ns[lang]

        type: ReminderType
        if today_day == remind.day and today_month == remind.month:
            type = ReminderType.OnTheDay
        else:
            type = ReminderType.BeforehandInOneDay

        try:
            completed_birthday_remind = await get_completed_birthday_remind(
                remind.id,
                today.year,
                type,
            )

            logger.debug(
                f"Completed birthday remind found: {completed_birthday_remind}. Skipping."
            )

            continue
        except IDForYearAndTypeNotFound as err:
            logger.debug(err)

        if type is ReminderType.OnTheDay:
            logger.debug(
                "Today is birthday",
                extra={"birthday_remind": remind},
            )

            text = l10n.format_value("birthday-today", {"name": remind.name})
        else:
            logger.debug(
                "Birthday is coming soon",
                extra={"birthday_remind": remind},
            )

            text = l10n.format_value(
                "birthday-coming-soon",
                {"name": remind.name},
            )

        await send_message_with_retries(
            bot,
            user.tg_id,
            text,
            parse_mode=None,
        )

        await add_completed_birthday_remind(
            CompletedBirthdayRemind(uuid7(), remind.id, today.year, type)
        )

        queue.task_done()

        await asyncio.sleep(0.03)
