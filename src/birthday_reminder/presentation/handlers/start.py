from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, invert_f
from aiogram.types import Message, User
from aiogram_dialog import DialogManager, StartMode
from uuid6 import uuid7

from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.application.user import UserRepo
from birthday_reminder.application.user.commands import AddUser
from birthday_reminder.domain.user.entities import User as UserDB

from ..dialogs.states import MainMenu, SelectLanguage
from ..filters import is_new_user_filter

__all__ = ["router"]

logger = getLogger(__name__)

router = Router(name="start_router")


@router.message(Command("start", "help", "menu"), is_new_user_filter)
async def start_for_new_user(
    message: Message,
    dialog_manager: DialogManager,
    user: User,
    uow: UnitOfWork,
    user_repo: UserRepo,
    language_code: str,
) -> None:
    logger.debug("Start command for new user")

    command = AddUser(user_repo, uow)

    await command(
        UserDB(id=uuid7(), language_code=language_code, tg_id=user.id)
    )

    logger.debug("User added to the database")

    await dialog_manager.start(
        SelectLanguage.select,
        mode=StartMode.RESET_STACK,
    )


@router.message(Command("start", "help", "menu"), invert_f(is_new_user_filter))
async def start_for_known_user(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    logger.debug("Start command for known user")

    await dialog_manager.start(
        MainMenu.menu,
        mode=StartMode.RESET_STACK,
    )
