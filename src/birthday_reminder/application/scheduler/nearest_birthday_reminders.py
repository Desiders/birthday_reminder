import asyncio
from asyncio import Queue
from calendar import isleap
from datetime import datetime, timedelta
from logging import getLogger

from birthday_reminder.application.birthday_remind.queries import (
    GetByInterval,
    GetByIntervalRequest,
)
from birthday_reminder.application.common.exceptions import RepoError
from birthday_reminder.config import Reminder as ReminderConfig
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind

logger = getLogger(__name__)


async def producer(
    config: ReminderConfig,
    queue: Queue[BirthdayRemind],
    get_by_interval: GetByInterval,
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
        now = datetime.now(tz=config.tz)

        # If the current hour is less than the hour set in the config, sleep until that hour.
        if now.hour < config.hour:
            config_datetime = config.get_datetime()
            remaining = config_datetime - now

            logger.debug(
                f"Sleeping until {config_datetime.strftime('%H:%M:%S')}. Remaining: {remaining}. Waiting for the configured hour."
            )

            await asyncio.sleep(remaining.total_seconds())

        # If today is 27 February, tomorrow is 28 February if it's a leap year, otherwise it's 1 March.
        # This need to be handled for cases when the current year isn't a leap year,
        # but we need to remind the user about the birthday of a person who was born on 29 February.
        # If the current year is a leap year, we don't need to handle this case because 29 February is a valid date.
        if now.month == 2 and now.day == 27:
            if isleap(now.year):
                tomorrow = now.replace(month=2, day=28, tzinfo=config.tz)
            else:
                tomorrow = now.replace(month=3, day=1, tzinfo=config.tz)
        # If today is 28 February, tomorrow is 29 February if it's a leap year, otherwise it's 1 March.
        elif now.month == 2 and now.day == 28:
            if isleap(now.year):
                tomorrow = now.replace(month=2, day=29, tzinfo=config.tz)
            else:
                tomorrow = now.replace(month=3, day=1, tzinfo=config.tz)
        # If today is 31 December, tomorrow is 1 January of the next year.
        elif now.month == 12 and now.day == 31:
            tomorrow = now.replace(
                year=now.year + 1, month=1, day=1, tzinfo=config.tz
            )
        # For all other cases, tomorrow is the next day or the next month if the next day is the first day of the next month.
        else:
            try:
                tomorrow = now.replace(day=now.day + 1, tzinfo=config.tz)
            except ValueError:
                tomorrow = now.replace(
                    month=now.month + 1, day=1, tzinfo=config.tz
                )

        start_day = now.day
        start_month = now.month
        end_day = tomorrow.day
        end_month = tomorrow.month

        logger.debug(
            f"Querying for reminders between {start_day}/{start_month} and {end_day}/{end_month}"
        )

        try:
            reminders = await get_by_interval(
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

        # Replace the current day with the next day and sleep until the hour set in the config
        next_day_with_config_hour = now.replace(
            hour=config.hour,
            minute=0,
            second=0,
            microsecond=0,
            fold=0,
        ) + timedelta(days=1)

        remaining = next_day_with_config_hour - now

        logger.debug(
            f"Sleeping until {next_day_with_config_hour.strftime('%H:%M:%S')}. "
            f"Remaining: {remaining}. Waiting for the next day."
        )

        await asyncio.sleep(remaining.total_seconds())
