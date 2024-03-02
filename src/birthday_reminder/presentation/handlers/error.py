from logging import getLogger

from aiogram.types import ErrorEvent, InaccessibleMessage, Message

from birthday_reminder.presentation.i18n import FormatText

logger = getLogger(__name__)


async def dialog_exception(
    event: ErrorEvent,
    format_text: FormatText,
) -> bool:
    update = event.update
    exc = event.exception

    text = format_text("dialog-error", None)

    if callback_query := update.callback_query:
        await callback_query.answer(text, show_alert=True, cache_time=60)

        match callback_query.message:
            case Message():
                logger.debug("Removing outdated message", exc_info=exc)

                await callback_query.message.delete()
            case InaccessibleMessage():
                logger.warn("Message is inaccessible", exc_info=exc)

            case None:
                logger.error("Callback query without message", exc_info=exc)
    else:
        logger.error("Unknown intent, but no callback query", exc_info=exc)

    return True
