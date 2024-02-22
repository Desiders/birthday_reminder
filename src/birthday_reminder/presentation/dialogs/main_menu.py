from logging import getLogger

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from .common import CREATE_REMIND_BUTTON
from .states import MainMenu

logger = getLogger(__name__)


async def show_capybara(
    callback_query: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    logger.debug("Show capybara")

    # TODO: implement capybara showing


main_menu = Dialog(
    Window(
        Const("Select action:"),
        CREATE_REMIND_BUTTON,
        Button(
            text=Const("Show capybara"),
            id="show_capybara",
            on_click=show_capybara,
        ),
        state=MainMenu.menu,
    ),
    name="main_menu",
)
