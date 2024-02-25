from logging import getLogger
from typing import Any, Literal
from uuid import UUID

from aiogram import Bot, F
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Row,
    ScrollingGroup,
    Select,
)
from aiogram_dialog.widgets.text import Format

from birthday_reminder.application.birthday_remind import (
    BirthdayRemindReader,
    BirthdayRemindRepo,
)
from birthday_reminder.application.birthday_remind.commands import (
    DeleteBirthdayRemindById,
)
from birthday_reminder.application.birthday_remind.queries import GetByUserID
from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.domain.birthday_remind.entities import BirthdayRemind
from birthday_reminder.domain.user.entities import User as UserDB
from birthday_reminder.presentation.i18n import (
    I18N_FORMAT_KEY,
    FormatText,
    I18NFormat,
)

from .common import MAIN_MENU_BUTTON
from .states import DeleteRemind, MainMenu

__all__ = ["delete_remind"]

REMINDERS_KEY = "reminders"
REMINDERS_COUNT_KEY = "reminders_count"
REMINDER_ID = "reminder"
GROUP_ID = "reminders_group"

logger = getLogger(__name__)


async def reminders_getter(dialog_manager: DialogManager, **_kwargs) -> dict:
    data = dialog_manager.middleware_data
    db_user: UserDB = data["db_user"]
    uow: UnitOfWork = data["uow"]
    birthday_remind_reader: BirthdayRemindReader = data[
        "birthday_remind_reader"
    ]

    query = GetByUserID(birthday_remind_reader, uow)

    reminders = await query(db_user.id)

    return {REMINDERS_KEY: reminders, REMINDERS_COUNT_KEY: len(reminders)}


def reminder_id_getter(reminder: BirthdayRemind) -> str:
    return str(reminder.id)


async def on_remind_selected(
    callback: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
) -> None:
    manager.dialog_data["remind_id"] = UUID(selected_item)

    await manager.next()


async def remind_info_getter(
    dialog_manager: DialogManager, **_kwargs
) -> dict[Literal["reminder_id"], UUID]:
    remind_id: UUID = dialog_manager.dialog_data["remind_id"]

    return {"reminder_id": remind_id}


async def delete_remind_confirmed(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """
    Handler for the confirm button.
    The handler sends a message to the user with the information about the deleted reminder and deletes the reminder from the database.

    Args:
        callback_query: The callback query with the user's confirmation.
        button: The button that triggered the handler.
        manager: The dialog manager.
    """
    data = manager.middleware_data
    uow: UnitOfWork = data["uow"]
    birthday_remind_repo: BirthdayRemindRepo = data["birthday_remind_repo"]

    reminder_info = await remind_info_getter(manager)

    reminder_id: UUID = reminder_info["reminder_id"]

    command = DeleteBirthdayRemindById(birthday_remind_repo, uow)

    logger.debug(
        "Delete reminder from the database",
        extra={
            "reminder_info": reminder_info,
        },
    )

    await command(reminder_id)

    format_text: FormatText = manager.middleware_data[I18N_FORMAT_KEY]
    text = format_text("delete-remind-success", None)

    match callback_query.message:
        case Message():
            logger.debug("Delete the message with the reminder confirmation")

            await callback_query.message.delete()

            logger.debug("Send message about successful reminder deletion")

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

    await manager.start(
        MainMenu.menu,
        mode=StartMode.RESET_STACK,
    )


delete_remind = Dialog(
    Window(
        I18NFormat("delete-remind-select-remind", when=F[REMINDERS_COUNT_KEY]),
        ScrollingGroup(
            Select(
                text=Format("{item.name}"),
                id=REMINDER_ID,
                item_id_getter=reminder_id_getter,
                items=REMINDERS_KEY,
                on_click=on_remind_selected,
            ),
            id=GROUP_ID,
            when=F[REMINDERS_COUNT_KEY],
            width=4,
            height=4,
        ),
        I18NFormat("reminders-empty", when=~F[REMINDERS_COUNT_KEY]),
        MAIN_MENU_BUTTON,
        getter=reminders_getter,
        state=DeleteRemind.select_remind,
    ),
    Window(
        I18NFormat("delete-remind-confirm"),
        Row(
            Back(I18NFormat("delete-remind-select-remind-button")),
            Button(
                text=I18NFormat("confirm-button"),
                id="confirm",
                on_click=delete_remind_confirmed,
            ),
        ),
        state=DeleteRemind.confirm,
    ),
    name="delete_remind",
)
