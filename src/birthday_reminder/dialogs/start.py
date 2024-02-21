from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from .states import CreateRemind

__all__ = ["router"]

router = Router(name="start_router")


@router.message(CommandStart())
async def start_dialog(
    message: Message, dialog_manager: DialogManager
) -> None:
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
