from typing import Any, Awaitable, Callable

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from ..i18n import I18N_FORMAT_KEY


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
        if event.from_user:
            # lang = event.from_user.language_code
            lang = self.default_lang
        else:
            lang = self.default_lang
        if lang not in self.l10ns:
            lang = self.default_lang

        l10n = self.l10ns[lang]

        data[I18N_FORMAT_KEY] = l10n.format_value

        return await handler(event, data)
