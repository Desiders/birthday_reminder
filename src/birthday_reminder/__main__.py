import asyncio
from logging import getLogger

from aiogram import Bot, Dispatcher, Router
from aiogram_dialog import setup_dialogs

from .adapters.database import get_engine, get_session_factory
from .config import configure_logging, load_config_from_env
from .presentation.dialogs import create_remind_dialog, main_menu_dialog
from .presentation.handlers import start_router
from .presentation.middlewares import DatabaseMiddleware, UserMiddleware

logger = getLogger(__name__)


async def main():
    config = load_config_from_env()
    configure_logging(config.logging)

    logger.debug("Config loaded", extra={"config": config})

    bot = Bot(token=config.bot.token, parse_mode=None)

    main_router = Router(name="main_router")

    main_router.include_router(create_remind_dialog)
    main_router.include_router(main_menu_dialog)
    main_router.include_router(start_router)

    engine = get_engine(config.database)
    pool = get_session_factory(engine)

    for observer in main_router.observers.values():
        observer.outer_middleware.register(DatabaseMiddleware(pool))
        observer.outer_middleware.register(UserMiddleware())

    dispatcher = Dispatcher()
    dispatcher.include_router(main_router)

    setup_dialogs(dispatcher)

    allowed_updates = main_router.resolve_used_update_types()

    logger.info(
        "Starting bot",
        extra={"allowed_updates": allowed_updates},
    )

    await dispatcher.start_polling(bot, allowed_updates=allowed_updates)


if __name__ == "__main__":
    asyncio.run(main())
