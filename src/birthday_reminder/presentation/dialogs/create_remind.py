from dataclasses import dataclass
from logging import getLogger
from typing import Any, Literal

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    ContentType,
    InaccessibleMessage,
    Message,
)
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Group,
    Next,
    Row,
    Select,
)
from aiogram_dialog.widgets.text import Format
from uuid6 import uuid7

from birthday_reminder.application.birthday_remind import BirthdayRemindRepo
from birthday_reminder.application.birthday_remind.commands import (
    AddBirthdayRemind,
)
from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import (
    BirthdayRemind as BirthdayRemindDB,
)
from birthday_reminder.domain.user.entities import User as UserDB
from birthday_reminder.presentation.i18n import (
    I18N_FORMAT_KEY,
    FormatText,
    I18NFormat,
)

from .common import MAIN_MENU_BUTTON
from .states import CreateRemind, MainMenu

__all__ = ["create_remind"]

MONTHS_KEY = "months"
MONTH_ID = "month"
DAYS_KEY = "days"
DAY_ID = "day"

logger = getLogger(__name__)


@dataclass
class Month:
    number: int
    name: str

    def translate(self, format_text: FormatText) -> str:
        return format_text(self.name, None)


MONTHS = [
    Month(1, "January"),
    Month(2, "February"),
    Month(3, "March"),
    Month(4, "April"),
    Month(5, "May"),
    Month(6, "June"),
    Month(7, "July"),
    Month(8, "August"),
    Month(9, "September"),
    Month(10, "October"),
    Month(11, "November"),
    Month(12, "December"),
]


async def months_getter(dialog_manager: DialogManager, **_kwargs):
    format_text: FormatText = dialog_manager.middleware_data[I18N_FORMAT_KEY]

    return {
        MONTHS_KEY: [
            Month(month.number, month.translate(format_text))
            for month in MONTHS
        ]
    }


def month_number_getter(month: Month) -> int:
    return month.number


async def on_month_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
) -> None:
    manager.dialog_data["month_number"] = int(selected_item)

    await manager.next()


@dataclass
class Day:
    number: int


async def days_getter(
    dialog_manager: DialogManager, **_kwargs
) -> dict[Literal["days"], list[Day]]:
    month_number: int = dialog_manager.dialog_data["month_number"]

    logger.debug("Month number", extra={"month_number": month_number})

    if month_number in (1, 3, 5, 7, 8, 10, 12):
        return {DAYS_KEY: [Day(i) for i in range(1, 32)]}
    elif month_number == 2:
        # We allow 29 days for February, because it's also a valid date for leap years.
        return {DAYS_KEY: [Day(i) for i in range(1, 30)]}
    elif month_number in (4, 6, 9, 11):
        return {DAYS_KEY: [Day(i) for i in range(1, 31)]}

    logger.error("Invalid month number", extra={"month_number": month_number})

    raise ValueError(f"Invalid month number: {month_number}. Should be 1-12.")


def day_number_getter(day: Day) -> int:
    return day.number


async def on_day_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
) -> None:
    manager.dialog_data["day"] = int(selected_item)

    await manager.next()


async def name_handler(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
) -> None:
    """
    Handler for the name input widget.
    If user's input is empty, the handler sends a message to the user about it.
    If the user's input is too long (more than 1000 characters), the handler sends a message to the user about it.

    Args:
        message: The message with the user's input.
        widget: The widget that triggered the handler.
        manager: The dialog manager.
    """

    if message.text is None:
        logger.debug("Empty message")

        format_text: FormatText = manager.middleware_data[I18N_FORMAT_KEY]
        text = format_text("create-remind-select-user-empty", None)

        await message.answer(
            text,
            parse_mode=None,
            disable_web_page_preview=True,
            disable_notification=False,
        )

        return

    if len(message.text) > 100:
        logger.debug("Too long message")

        format_text: FormatText = manager.middleware_data[I18N_FORMAT_KEY]
        text = format_text("create-remind-select-user-too-long", None)

        await message.answer(
            text,
            parse_mode=None,
            disable_web_page_preview=True,
            disable_notification=False,
        )

        return

    manager.dialog_data["name"] = message.text

    logger.debug("Name input", extra={"message_text": message.text})

    await manager.next()


async def remind_info_getter(dialog_manager: DialogManager, **_kwargs) -> dict:
    month_number: int = dialog_manager.dialog_data["month_number"]
    month = next((m for m in MONTHS if m.number == month_number))

    day: int = dialog_manager.dialog_data["day"]
    name: str = dialog_manager.dialog_data["name"]

    return dict(
        month=month,
        day=day,
        name=name,
    )


async def create_remind_confirmed(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """
    Handler for the confirm button.
    The handler sends a message to the user with the information about the reminder and saves the reminder to the database.

    Args:
        callback_query: The callback query with the user's confirmation.
        button: The button that triggered the handler.
        manager: The dialog manager.
    """
    data = manager.middleware_data
    db_user: UserDB = data["db_user"]
    uow: UnitOfWork = data["uow"]
    birthday_remind_repo: BirthdayRemindRepo = data["birthday_remind_repo"]

    reminder_info = await remind_info_getter(manager)

    month: Month = reminder_info["month"]
    month_number = month.number
    day: int = reminder_info["day"]
    name: str = reminder_info["name"]

    command = AddBirthdayRemind(birthday_remind_repo, uow)

    logger.debug(
        "Add reminder to the database",
        extra={
            "reminder_info": reminder_info,
        },
    )

    await command(
        BirthdayRemindDB(
            id=uuid7(),
            user_id=db_user.id,
            name=name,
            month=month_number,
            day=day,
        )
    )

    format_text: FormatText = manager.middleware_data[I18N_FORMAT_KEY]
    text = format_text("create-remind-success", None)

    match callback_query.message:
        case Message():
            logger.debug("Delete the message with the reminder confirmation")

            await callback_query.message.delete()

            logger.debug("Send message about successful reminder creation")

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

            bot: Bot = manager.middleware_data["bot"]

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

    await manager.start(
        MainMenu.menu,
        mode=StartMode.RESET_STACK,
    )


create_remind = Dialog(
    Window(
        I18NFormat("create-remind-select-month"),
        Group(
            Select(
                text=Format("{item.name}"),
                id=MONTH_ID,
                item_id_getter=month_number_getter,
                items=MONTHS_KEY,
                on_click=on_month_selected,
            ),
            width=3,
        ),
        MAIN_MENU_BUTTON,
        getter=months_getter,
        state=CreateRemind.select_month,
    ),
    Window(
        I18NFormat("create-remind-select-day"),
        Group(
            Select(
                text=Format("{item.number}"),
                id=DAY_ID,
                item_id_getter=day_number_getter,
                items=DAYS_KEY,
                on_click=on_day_selected,
            ),
            width=6,
        ),
        Back(I18NFormat("create-remind-select-month-button")),
        getter=days_getter,
        state=CreateRemind.select_day,
    ),
    Window(
        I18NFormat("create-remind-select-user"),
        Back(I18NFormat("create-remind-select-day-button")),
        MessageInput(name_handler, content_types=ContentType.TEXT),
        state=CreateRemind.select_user,
        preview_add_transitions=[Next()],  # hint for graph rendering
    ),
    Window(
        I18NFormat("create-remind-confirm"),
        Row(
            Back(I18NFormat("create-remind-input-user-button")),
            Button(
                text=I18NFormat("confirm-button"),
                id="confirm",
                on_click=create_remind_confirmed,
            ),
        ),
        state=CreateRemind.confirm,
        getter=remind_info_getter,
    ),
    name="create_remind",
)
