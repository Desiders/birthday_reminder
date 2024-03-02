from logging import getLogger
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Format
from fluent.runtime import FluentLocalization

from birthday_reminder.application.birthday_remind import BirthdayRemindReader
from birthday_reminder.application.birthday_remind.queries import GetByUserID
from birthday_reminder.application.common import UnitOfWork
from birthday_reminder.application.user import UserRepo
from birthday_reminder.application.user.commands import UpdateUser
from birthday_reminder.config import Config, Locale
from birthday_reminder.domain.user.entities import User as UserDB
from birthday_reminder.presentation.i18n import (
    I18N_FORMAT_KEY,
    L10NS_KEY,
    I18NFormat,
)

from .states import CreateRemind, MainMenu, SelectLanguage

LANGUAGES_KEY = "languages"
LANGUAGE_ID = "language"
GROUP_ID = "languages_group"

logger = getLogger(__name__)


async def languages_getter(
    dialog_manager: DialogManager, config: Config, **_kwargs
) -> dict:
    first_name = (
        dialog_manager.event.from_user.full_name
        if dialog_manager.event.from_user
        else "capybara"
    )

    return {
        LANGUAGES_KEY: config.localization.locales,
        "first_name": first_name,
    }


def language_code_getter(locale: Locale) -> str:
    return locale.code


async def on_language_selected(
    callback_query: CallbackQuery,
    widget: Any,
    manager: DialogManager,
    selected_item: str,
) -> None:
    logger.debug("Language selected")

    data = manager.middleware_data
    db_user: UserDB = data["db_user"]
    uow: UnitOfWork = data["uow"]
    user_repo: UserRepo = data["user_repo"]
    birthday_remind_reader: BirthdayRemindReader = data[
        "birthday_remind_reader"
    ]
    l10ns: dict[str, FluentLocalization] = data[L10NS_KEY]
    l10n = l10ns[selected_item]

    manager.middleware_data[L10NS_KEY] = l10n
    manager.middleware_data[I18N_FORMAT_KEY] = l10n.format_value

    command = UpdateUser(user_repo, uow)

    logger.debug(
        "Update user language", extra={"language_code": selected_item}
    )

    query = GetByUserID(birthday_remind_reader, uow)

    await command(
        UserDB(id=db_user.id, language_code=selected_item, tg_id=db_user.tg_id)
    )

    logger.debug("Get birthday reminds")

    birthday_reminders = await query(db_user.id)

    if not birthday_reminders:
        await manager.start(
            CreateRemind.select_month,
            mode=StartMode.RESET_STACK,
        )
    else:
        await manager.start(
            MainMenu.menu,
            mode=StartMode.RESET_STACK,
        )


select_language = Dialog(
    Window(
        I18NFormat("start"),
        Group(
            Select(
                text=Format("{item.label}"),
                id=LANGUAGE_ID,
                item_id_getter=language_code_getter,
                items=LANGUAGES_KEY,
                on_click=on_language_selected,
            ),
            id=GROUP_ID,
            width=2,
        ),
        state=SelectLanguage.select,
        getter=languages_getter,
    ),
    name="select_language",
)
