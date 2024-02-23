from logging import getLogger
from uuid import UUID

from aiogram import Bot, F
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    ManagedRadio,
    Next,
    Radio,
    Row,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Const, Format

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


def remind_is_checked(
    data: dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    radio: ManagedRadio = dialog_manager.find(REMINDER_ID)  # type: ignore

    return radio.get_checked() is not None


async def remind_info_getter(dialog_manager: DialogManager, **_kwargs) -> dict:
    radio: ManagedRadio = dialog_manager.find(REMINDER_ID)  # type: ignore
    reminder_id = UUID(radio.get_checked())  # type: ignore

    return dict(
        reminder_id=reminder_id,
    )


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

    text = (
        "You have deleted a reminder.\n\n"
        "If you want to create reminder or manage existing ones, use buttons below."
    )

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
        Const(
            "Select the reminder you want to delete:",
            when=F[REMINDERS_COUNT_KEY],
        ),
        ScrollingGroup(
            Radio(
                checked_text=Format("🔘 {item.name}"),
                unchecked_text=Format("{item.name}"),
                id=REMINDER_ID,
                item_id_getter=reminder_id_getter,
                items=REMINDERS_KEY,
            ),
            id=GROUP_ID,
            when=F[REMINDERS_COUNT_KEY],
            width=4,
            height=4,
        ),
        Const(
            "You don't have any reminders yet 🐨",
            when=~F[REMINDERS_COUNT_KEY],
        ),
        Row(
            MAIN_MENU_BUTTON,
            Next(
                text=Const("Delete user >>"),
                when=remind_is_checked,
            ),
        ),
        getter=reminders_getter,
        state=DeleteRemind.select_remind,
    ),
    Window(
        Format("You are about to delete the reminder?"),
        Row(
            Back(
                text=Const("<< Select reminder"),
            ),
            Button(
                text=Const("Confirm >>"),
                id="confirm",
                on_click=delete_remind_confirmed,
            ),
        ),
        state=DeleteRemind.confirm,
    ),
    name="delete_remind",
)
