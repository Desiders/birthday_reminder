from aiogram_dialog.widgets.kbd import Start

from birthday_reminder.presentation.i18n import I18NFormat

from .states import CreateRemind, MainMenu

MAIN_MENU_BUTTON = Start(
    text=I18NFormat("back-to-main-menu-button"),
    id="main_menu",
    state=MainMenu.menu,
)

CREATE_REMIND_BUTTON = Start(
    text=I18NFormat("create-remind-button"),
    id="create_remind",
    state=CreateRemind.select_month,
)
