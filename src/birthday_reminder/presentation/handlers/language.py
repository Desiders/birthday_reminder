from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, invert_f
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from ..dialogs.states import SelectLanguage
from ..filters import is_new_user_filter

__all__ = ["router"]

logger = getLogger(__name__)

router = Router(name="language_router")


@router.message(Command("language", "lang"), invert_f(is_new_user_filter))
async def select_language(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    logger.debug("Start command for known user")

    await dialog_manager.start(
        SelectLanguage.select,
        mode=StartMode.RESET_STACK,
    )
