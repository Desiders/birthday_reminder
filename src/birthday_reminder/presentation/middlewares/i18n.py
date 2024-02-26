from logging import getLogger
from typing import Any, Awaitable, Callable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from birthday_reminder.domain.user.entities import User as UserDB

from ..i18n.constants import I18N_FORMAT_KEY, L10NS_KEY, LANG_CODE_KEY

logger = getLogger(__name__)


class I18nMiddleware(BaseMiddleware):
    def __init__(
        self,
        l10ns: dict[str, FluentLocalization],
        default_lang: str,
    ):
        super().__init__()

        self.l10ns = l10ns
        self.default_lang = default_lang

    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        db_user: UserDB | None = data.get("db_user")
        if db_user:
            lang = db_user.language_code

            logger.debug("User language code from db", extra={"lang": lang})
        elif event.from_user:
            lang = event.from_user.language_code

            logger.debug("User language code from event", extra={"lang": lang})

        if not lang:
            lang = self.default_lang

            logger.debug("Using default language", extra={"lang": lang})
        elif lang not in self.l10ns:
            lang = self.default_lang

            logger.debug(
                "Language not found, using default", extra={"lang": lang}
            )

        l10n = self.l10ns[lang]

        data[L10NS_KEY] = self.l10ns
        data[I18N_FORMAT_KEY] = l10n.format_value
        data[LANG_CODE_KEY] = lang

        return await handler(event, data)
