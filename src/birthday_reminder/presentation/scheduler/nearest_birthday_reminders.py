from asyncio import Queue
from datetime import date
from logging import getLogger

from aiogram import Bot

from birthday_reminder.application.common.exceptions import RepoError
from birthday_reminder.application.user.queries import GetByID
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind
from birthday_reminder.domain.user.exceptions import IDNotFound

logger = getLogger(__name__)


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

        await bot.send_message(
            user.tg_id,
            text,
            parse_mode=None,
            disable_web_page_preview=True,
            disable_notification=False,
        )

        queue.task_done()
