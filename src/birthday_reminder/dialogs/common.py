from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from .states import CreateRemind, MainMenu

MAIN_MENU_BUTTON = Start(
    text=Const("<< Menu"),
    id="main_menu",
    state=MainMenu.menu,
)

CREATE_REMIND_BUTTON = Start(
    text=Const("Create reminder"),
    id="create_remind",
    state=CreateRemind.select_month,
)
