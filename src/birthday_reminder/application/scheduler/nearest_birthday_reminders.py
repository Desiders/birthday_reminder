import asyncio
from asyncio import Queue
from calendar import isleap
from datetime import date
from logging import getLogger

from birthday_reminder.application.birthday_remind.queries import (
    GetByInterval,
    GetByIntervalRequest,
)
from birthday_reminder.application.common.exceptions import RepoError
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind

TIMEOUT_BETWEEN_REQUESTS = 60 * 60 * 24.0  # 24 hours in seconds

logger = getLogger(__name__)


async def producer(
    queue: Queue[BirthdayRemind],
    query: GetByInterval,
) -> None:
    """
    This function is a producer that queries the database for birthday reminders that are due in the next 24 hours and
    puts them in the queue.

    :param queue: The queue where the birthday reminders will be put.
    :param query: The query to be used to get the birthday reminders.

    :return: None
    """

    logger.info("Starting the producer")

    while True:
        today = date.today()

        # If today is 27 February, tomorrow is 28 February if it's a leap year, otherwise it's 1 March.
        # This need to be handled for cases when the current year isn't a leap year,
        # but we need to remind the user about the birthday of a person who was born on 29 February.
        # If the current year is a leap year, we don't need to handle this case because 29 February is a valid date.
        if today.month == 2 and today.day == 27:
            if isleap(today.year):
                tomorrow = today.replace(month=2, day=28)
            else:
                tomorrow = today.replace(month=3, day=1)
        # If today is 28 February, tomorrow is 29 February if it's a leap year, otherwise it's 1 March.
        elif today.month == 2 and today.day == 28:
            if isleap(today.year):
                tomorrow = today.replace(month=2, day=29)
            else:
                tomorrow = today.replace(month=3, day=1)
        # If today is 31 December, tomorrow is 1 January of the next year.
        elif today.month == 12 and today.day == 31:
            tomorrow = today.replace(year=today.year + 1, month=1, day=1)
        # For all other cases, tomorrow is the next day or the next month if the next day is the first day of the next month.
        else:
            try:
                tomorrow = today.replace(day=today.day + 1)
            except ValueError:
                tomorrow = today.replace(month=today.month + 1, day=1)

        start_day = today.day
        start_month = today.month
        end_day = tomorrow.day
        end_month = tomorrow.month

        logger.debug(
            f"Querying for reminders between {start_day}/{start_month} and {end_day}/{end_month}"
        )

        try:
            reminders = await query(
                GetByIntervalRequest(
                    start_day, start_month, end_day, end_month
                )
            )
        except RepoError as err:
            logger.error(
                "Error while getting reminders by interval", exc_info=err
            )

            await asyncio.sleep(5)

            continue
        except Exception as err:
            logger.critical(
                "Unknown error while getting reminders by interval",
                exc_info=err,
            )

            await asyncio.sleep(5)

            continue

        logger.debug(f"Reminders count: {len(reminders)}")

        for reminder in reminders:
            logger.debug(f"Produced: {reminder}")

            await queue.put(reminder)

        await asyncio.sleep(TIMEOUT_BETWEEN_REQUESTS)
