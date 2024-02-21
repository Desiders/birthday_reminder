import asyncio
from logging import getLogger

from aiogram import Bot, Dispatcher, Router
from aiogram_dialog import setup_dialogs

from .config import configure_logging, load_config_from_env
from .dialogs import create_reming_dialog, main_menu_dialog, start_router

logger = getLogger(__name__)


async def main():
    config = load_config_from_env()
    configure_logging(config.logging)

    logger.debug("Config loaded", extra={"config": config})

    bot = Bot(token=config.bot.token, parse_mode=None)

    main_router = Router(name="main_router")

    dispatcher = Dispatcher()

    dispatcher.include_router(main_router)
    main_router.include_router(start_router)
    main_router.include_router(create_reming_dialog)
    main_router.include_router(main_menu_dialog)

    setup_dialogs(dispatcher)

    allowed_updates = main_router.resolve_used_update_types()

    logger.info(
        "Starting bot",
        extra={"allowed_updates": allowed_updates},
    )

    await dispatcher.start_polling(bot, allowed_updates=allowed_updates)


if __name__ == "__main__":
    asyncio.run(main())
