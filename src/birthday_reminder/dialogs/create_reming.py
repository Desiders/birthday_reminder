from dataclasses import dataclass
from logging import getLogger
from typing import Literal

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    ContentType,
    InaccessibleMessage,
    Message,
)
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Group,
    ManagedRadio,
    Next,
    Radio,
    Row,
)
from aiogram_dialog.widgets.text import Const, Format

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


async def months_getter(**_kwargs):
    return {MONTHS_KEY: MONTHS}


def month_number_getter(month: Month) -> int:
    return month.number


def month_is_checked(
    data: dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    radio: ManagedRadio = dialog_manager.find(MONTH_ID)  # type: ignore

    return radio.get_checked() is not None


@dataclass
class Day:
    number: int


async def days_getter(
    dialog_manager: DialogManager, **_kwargs
) -> dict[Literal["days"], list[Day]]:
    radio: ManagedRadio = dialog_manager.find(MONTH_ID)  # type: ignore
    month_number: int = int(radio.get_checked())  # type: ignore

    logger.debug("Month number", extra={"month_number": month_number})

    if month_number in (1, 3, 5, 7, 8, 10, 12):
        return {DAYS_KEY: [Day(i) for i in range(1, 32)]}
    elif month_number == 2:
        return {DAYS_KEY: [Day(i) for i in range(1, 29)]}
    elif month_number in (4, 6, 9, 11):
        return {DAYS_KEY: [Day(i) for i in range(1, 31)]}

    logger.error("Invalid month number", extra={"month_number": month_number})

    raise ValueError(f"Invalid month number: {month_number}. Should be 1-12.")


def day_number_getter(month: Month) -> int:
    return month.number


def day_is_checked(
    data: dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    radio: ManagedRadio = dialog_manager.find(DAY_ID)  # type: ignore

    return radio.get_checked() is not None


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

        await message.answer(
            "Input the name of syour friend. It can't be empty."
        )

        return

    if len(message.text) > 1000:
        logger.debug("Too long message")

        await message.answer(
            "The name of your friend is too long. It should be less than 1000 characters."
        )
        return

    manager.dialog_data["name"] = message.text

    logger.debug("Name input", extra={"message_text": message.text})

    await manager.next()


async def remind_info_getter(dialog_manager: DialogManager, **_kwargs) -> dict:
    radio: ManagedRadio = dialog_manager.find(MONTH_ID)  # type: ignore
    month_number = int(radio.get_checked())  # type: ignore
    month = next((m for m in MONTHS if m.number == month_number))

    radio = dialog_manager.find(DAY_ID)  # type: ignore
    day_number = int(radio.get_checked())  # type: ignore

    name = dialog_manager.dialog_data["name"]

    return dict(
        month=month,
        day_number=day_number,
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

    reminder_info = await remind_info_getter(manager)

    logger.debug(
        "Create reminder",
        extra={
            "reminder_info": reminder_info,
        },
    )

    text = (
        "Congratulations! You have created a reminder for your friend.\n"
        "I will notify you on the day of the event.\n\n"
        "If you want to create another reminder or manage existing ones, "
        "use buttons below."
    )

    match callback_query.message:
        case Message():
            logger.debug("Delete the message with the reminder confirmation")

            await callback_query.message.delete()

            logger.debug("Send message about successful reminder creation")

            # TODO: save reminder to the database

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

            # TODO: save reminder to the database

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

    await manager.start(
        MainMenu.menu,
        mode=StartMode.RESET_STACK,
    )


create_remind = Dialog(
    Window(
        Const("Select the month of your friend's birth:"),
        Group(
            Radio(
                checked_text=Format("🔘 {item.name}"),
                unchecked_text=Format("{item.name}"),
                id=MONTH_ID,
                item_id_getter=month_number_getter,
                items=MONTHS_KEY,
            ),
            width=3,
        ),
        Row(
            MAIN_MENU_BUTTON,
            Next(
                text=Const("Select day >>"),
                when=month_is_checked,
            ),
        ),
        getter=months_getter,
        state=CreateRemind.select_month,
    ),
    Window(
        Const("Select the day of your friend's birth:"),
        Group(
            Radio(
                checked_text=Format("🔘 {item.number}"),
                unchecked_text=Format("{item.number}"),
                id=DAY_ID,
                item_id_getter=day_number_getter,
                items=DAYS_KEY,
            ),
            width=6,
        ),
        Row(
            Back(
                text=Const("<< Select month"),
            ),
            Next(
                text=Const("Input user >>"),
                when=day_is_checked,
            ),
        ),
        getter=days_getter,
        state=CreateRemind.select_day,
    ),
    Window(
        Const("Input the name of your friend:"),
        Back(
            text=Const("<< Select day"),
        ),
        MessageInput(name_handler, content_types=ContentType.TEXT),
        state=CreateRemind.select_user,
        preview_add_transitions=[Next()],  # hint for graph rendering
    ),
    Window(
        Format(
            "You are about to create a reminder for {name} on {day_number} {month.name}?"
        ),
        Row(
            Back(
                text=Const("<< Input user"),
            ),
            Button(
                text=Const("Confirm >>"),
                id="confirm",
                on_click=create_remind_confirmed,
            ),
        ),
        state=CreateRemind.confirm,
        getter=remind_info_getter,
    ),
    name="create_remind",
)
