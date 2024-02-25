from logging import getLogger
from typing import Literal

from aiogram.types import ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Back, Next, Row, Start
from aiogram_dialog.widgets.media import DynamicMedia

from birthday_reminder.config import Config
from birthday_reminder.presentation.i18n import I18NFormat

from .common import CREATE_REMIND_BUTTON
from .states import DeleteRemind, MainMenu, ShowReminders

logger = getLogger(__name__)


async def capybara_getter(
    dialog_manager: DialogManager,
    config: Config,
    **kwargs,
) -> dict[Literal["capybara"], MediaAttachment]:
    return {
        "capybara": MediaAttachment(
            path=str(config.media.capybara_path),
            type=ContentType.PHOTO,
        )
    }


main_menu = Dialog(
    Window(
        I18NFormat("main-menu"),
        CREATE_REMIND_BUTTON,
        Row(
            Start(
                text=I18NFormat("main-menu-show-reminders"),
                id="show_reminders",
                state=ShowReminders.show,
            ),
            Start(
                text=I18NFormat("main-menu-delete-reminder"),
                id="delete_remind",
                state=DeleteRemind.select_remind,
            ),
        ),
        Next(I18NFormat("main-menu-show-capybara")),
        state=MainMenu.menu,
    ),
    Window(
        I18NFormat("show-capybara"),
        Back(I18NFormat("show-capybara-back")),
        DynamicMedia("capybara"),
        state=MainMenu.capybara,
        getter=capybara_getter,
    ),
    name="main_menu",
)
