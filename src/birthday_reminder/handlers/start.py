from logging import getLogger

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from ..dialogs.create_reming import CreateRemind

__all__ = ["router"]

logger = getLogger(__name__)

router = Router(name="start_router")


@router.message(CommandStart())
async def start(message: Message, dialog_manager: DialogManager) -> None:
    logger.debug("Start command")

    first_name: str
    if message.from_user:
        first_name = message.from_user.first_name
    else:
        first_name = "capybara"

    is_new_user = True  # TODO: check if user is new

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

    await dialog_manager.start(
        CreateRemind.select_month,
        mode=StartMode.RESET_STACK,
    )
