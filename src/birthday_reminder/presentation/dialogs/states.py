from aiogram.fsm.state import State, StatesGroup


class MainMenu(StatesGroup):
    menu = State()


class CreateRemind(StatesGroup):
    select_month = State()
    select_day = State()
    select_user = State()
    confirm = State()


class ShowReminders(StatesGroup):
    show = State()


class DeleteRemind(StatesGroup):
    select_remind = State()
    confirm = State()
