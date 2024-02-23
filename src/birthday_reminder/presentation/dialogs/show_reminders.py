from datetime import date
from logging import getLogger

from aiogram import F
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.birthday_remind.queries import (
    GetByUserIDAndSortByNearest,
    GetByUserIDAndSortByNearestRequest,
)
from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.domain.user.entities import User as UserDB

from .common import MAIN_MENU_BUTTON
from .states import ShowReminders

__all__ = ["show_reminders"]

REMINDERS_TEXT_KEY = "reminders"
REMINDERS_COUNT_KEY = "reminders_count"

logger = getLogger(__name__)


async def reminders_getter(dialog_manager: DialogManager, **_kwargs) -> dict:
    data = dialog_manager.middleware_data
    db_user: UserDB = data["db_user"]
    uow: UnitOfWork = data["uow"]
    birthday_remind_reader: BirthdayRemindReader = data[
        "birthday_remind_reader"
    ]

    query = GetByUserIDAndSortByNearest(birthday_remind_reader, uow)

    today = date.today()

    reminders = await query(
        GetByUserIDAndSortByNearestRequest(db_user.id, today.day, today.month)
    )

    texts = []

    for number, remind in enumerate(reminders, start=1):
        # Get datetime of the birthday by its day and month.
        try:
            birth_date = date(today.year, remind.month, remind.day)

            # If birthday have already been this year, then add 1 year to the date.
            # If the date can't be in the next year (extra day of leap year), then minus 1 day.
            if birth_date < today:
                try:
                    birth_date = date(today.year + 1, remind.month, remind.day)
                except ValueError:
                    birth_date = date(
                        today.year + 1, remind.month, remind.day - 1
                    )

                    difference = birth_date - today

                    texts.append(
                        f"{number}) {remind.name}, ~{birth_date.strftime('%d.%m')} (in ~{difference.days} days, not leap year)"
                    )

                    continue

            difference = birth_date - today

            texts.append(
                f"{number}) {remind.name}, {birth_date.strftime('%d.%m')} (in {difference.days} days)"
            )
        except ValueError:
            # If the date is can't be in this year (extra day of leap year), then minus 1 day.
            birth_date = date(today.year, remind.month, remind.day - 1)

            # If birthday have already been this year, then add 1 year to the date.
            # If the date can't be in the next year (extra day of leap year), then minus 1 day.
            if birth_date < today:
                try:
                    birth_date = date(today.year + 1, remind.month, remind.day)

                    difference = birth_date - today

                    texts.append(
                        f"{number}) {remind.name}, {birth_date.strftime('%d.%m')} (in {difference.days} days)"
                    )

                    continue
                except ValueError:
                    birth_date = date(
                        today.year + 1, remind.month, remind.day - 1
                    )

            difference = birth_date - today

            texts.append(
                f"{number}) {remind.name}, ~{birth_date.strftime('%d.%m')} (in ~{difference.days} days, not leap year)"
            )

    return {
        REMINDERS_TEXT_KEY: "\n".join(texts),
        REMINDERS_COUNT_KEY: len(reminders),
    }


show_reminders = Dialog(
    Window(
        Format("Your reminders:\n\n{reminders}", when=F[REMINDERS_COUNT_KEY]),
        Const(
            "You don't have any reminders yet 🐨",
            when=~F[REMINDERS_COUNT_KEY],
        ),
        MAIN_MENU_BUTTON,
        getter=reminders_getter,
        state=ShowReminders.show,
    ),
    name="show_reminders",
)
