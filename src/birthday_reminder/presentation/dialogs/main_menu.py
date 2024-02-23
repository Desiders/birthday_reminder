from datetime import date
from logging import getLogger

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
)
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.birthday_remind.queries import (
    GetByUserIDAndSortByNearest,
    GetByUserIDAndSortByNearestRequest,
)
from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.domain.user.entities import User as UserDB

from .common import CREATE_REMIND_BUTTON
from .states import CreateRemind, MainMenu

logger = getLogger(__name__)


async def show_capybara(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    logger.debug("Show capybara")

    # TODO: implement capybara showing


async def show_reminders(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    logger.debug("Show reminders")

    data = manager.middleware_data
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

    if len(reminders) == 0:
        logger.debug("Send message with no reminders")

        text = (
            "You don't have any reminders yet."
            "Let's start by creating a reminder."
        )

        await manager.start(
            CreateRemind.select_month,
            mode=StartMode.RESET_STACK,
        )

        return

    text = "Your reminders:\n\n"

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

                    text += f"{number}) {remind.name}, ~{birth_date.strftime('%d.%m')} (in ~{difference.days} days, not leap year)\n"

                    continue

            difference = birth_date - today

            text += f"{number}) {remind.name}, {birth_date.strftime('%d.%m')} (in {difference.days} days)\n"
        except ValueError:
            # If the date is can't be in this year (extra day of leap year), then minus 1 day.
            birth_date = date(today.year, remind.month, remind.day - 1)

            # If birthday have already been this year, then add 1 year to the date.
            # If the date can't be in the next year (extra day of leap year), then minus 1 day.
            if birth_date < today:
                try:
                    birth_date = date(today.year + 1, remind.month, remind.day)

                    difference = birth_date - today

                    text += f"{number}) {remind.name}, {birth_date.strftime('%d.%m')} (in {difference.days} days)\n"

                    continue
                except ValueError:
                    birth_date = date(
                        today.year + 1, remind.month, remind.day - 1
                    )

            difference = birth_date - today

            text += f"{number}) {remind.name}, ~{birth_date.strftime('%d.%m')} (in ~{difference.days} days, not leap year)\n"

    match callback_query.message:
        case Message():
            logger.debug("Send message with reminders")

            await callback_query.message.answer(
                text=text,
                parse_mode=None,
                disable_web_page_preview=True,
                disable_notification=False,
            )
        case InaccessibleMessage():
            logger.warn(
                "Inaccessible message. Try to send a message in private chat."
            )

            bot: Bot = manager.middleware_data["bot"]  # type: ignore

            await bot.send_message(
                callback_query.from_user.id,
                text=text,
                parse_mode=None,
                disable_web_page_preview=True,
                disable_notification=False,
            )
        case None:
            logger.error(
                "Message does not exist",
                extra={"callback_query": callback_query},
            )

            raise NotImplementedError(
                "This should not happen, because `message` always has a value in this case."
            )


main_menu = Dialog(
    Window(
        Const("Select action:"),
        CREATE_REMIND_BUTTON,
        Button(
            text=Const("Show capybara"),
            id="show_capybara",
            on_click=show_capybara,
        ),
        Button(
            text=Const("Show reminders"),
            id="show_reminders",
            on_click=show_reminders,
        ),
        state=MainMenu.menu,
    ),
    name="main_menu",
)
