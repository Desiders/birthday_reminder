from logging import getLogger

from aiogram import Router
from aiogram.filters import CommandStart, invert_f
from aiogram.types import Message, User
from aiogram_dialog import DialogManager, StartMode
from uuid6 import uuid7

from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.application.user import UserRepo
from birthday_reminder.application.user.commands import AddUser
from birthday_reminder.domain.user.entities import User as UserDB

from ..dialogs.states import CreateRemind, MainMenu
from ..filters import is_new_user_filter

__all__ = ["router"]

logger = getLogger(__name__)

router = Router(name="start_router")


@router.message(CommandStart(), is_new_user_filter)
async def start_for_new_user(
    message: Message,
    dialog_manager: DialogManager,
    user: User,
    uow: UnitOfWork,
    user_repo: UserRepo,
) -> None:
    logger.debug("Start command for new user")

    first_name: str
    if message.from_user:
        first_name = message.from_user.first_name
    else:
        first_name = "capybara"

    text = (
        f"Hello, {first_name}!\n\n"
        "I can help you remember your friends' birthdays. "
        "Let's start by creating a reminder."
    )

    await message.answer(
        text,
        parse_mode=None,
        disable_web_page_preview=True,
        disable_notification=False,
    )

    command = AddUser(user_repo, uow)

    await command(UserDB(id=uuid7(), tg_id=user.id))

    logger.debug("User added to the database")

    await dialog_manager.start(
        CreateRemind.select_month,
        mode=StartMode.RESET_STACK,
    )


@router.message(CommandStart(), invert_f(is_new_user_filter))
async def start_for_known_user(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    logger.debug("Start command for known user")

    await dialog_manager.start(
        MainMenu.menu,
        mode=StartMode.RESET_STACK,
    )
