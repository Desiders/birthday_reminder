from logging import getLogger
from typing import Literal

from aiogram.types import ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Back, Next, Row, Start
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const

from birthday_reminder.config import Config

from .common import CREATE_REMIND_BUTTON
from .states import DeleteRemind, MainMenu, ShowReminders

logger = getLogger(__name__)


async def capybara_getter(
    dialog_manager: DialogManager,
    config: Config,
    **kwargs,
) -> dict[Literal["capybara"], MediaAttachment]:
    logger.debug("capybara_getter", extra={"_config": config})

    return {
        "capybara": MediaAttachment(
            path=str(config.media.capybara_path),
            type=ContentType.PHOTO,
        )
    }


main_menu = Dialog(
    Window(
        Const("Select action:"),
        CREATE_REMIND_BUTTON,
        Row(
            Start(
                text=Const("Show reminders"),
                id="show_reminders",
                state=ShowReminders.show,
            ),
            Start(
                text=Const("Delete reminder"),
                id="delete_remind",
                state=DeleteRemind.select_remind,
            ),
        ),
        Next(
            text=Const("Show capybara"),
            id="show_capybara",
        ),
        state=MainMenu.menu,
    ),
    Window(
        Const("Capybara see you"),
        Back(
            Const("Oh no, I'm scared!"),
            id="main_menu",
        ),
        DynamicMedia("capybara"),
        state=MainMenu.capybara,
        getter=capybara_getter,
    ),
    name="main_menu",
)
