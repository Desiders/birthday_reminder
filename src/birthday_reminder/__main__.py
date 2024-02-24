import asyncio
from logging import getLogger

from aiogram import Bot, Dispatcher, Router
from aiogram_dialog import setup_dialogs

from birthday_reminder.adapters.database import SQLAlchemyUoW
from birthday_reminder.adapters.database.repositories import (
    BirthdayRemindReaderImpl,
    UserReaderImpl,
)
from birthday_reminder.application.birthday_remind.queries import (
    GetByInterval,
)
from birthday_reminder.application.user.queries import GetByID

from .adapters.database import get_engine, get_session_factory
from .application.scheduler import nearest_birthday_reminders_producer
from .config import configure_logging, load_config_from_env
from .presentation.dialogs import (
    create_remind_dialog,
    delete_remind_dialog,
    main_menu_dialog,
    show_reminders_dialog,
)
from .presentation.handlers import start_router, stats_router
from .presentation.middlewares import DatabaseMiddleware, UserMiddleware
from .presentation.scheduler import nearest_birthday_reminders_consumer

logger = getLogger(__name__)


async def main():
    config = load_config_from_env()
    configure_logging(config.logging)

    logger.debug("Config loaded", extra={"config": config})

    bot = Bot(token=config.bot.token, parse_mode=None)

    main_router = Router(name="main_router")

    main_router.include_router(start_router)
    main_router.include_router(stats_router)

    main_router.include_router(create_remind_dialog)
    main_router.include_router(main_menu_dialog)
    main_router.include_router(delete_remind_dialog)
    main_router.include_router(show_reminders_dialog)

    engine = get_engine(config.database)
    pool = get_session_factory(engine)

    for observer in main_router.observers.values():
        observer.outer_middleware.register(DatabaseMiddleware(pool))
        observer.outer_middleware.register(UserMiddleware())

    session = pool()

    queue = asyncio.Queue()
    birthday_reader = BirthdayRemindReaderImpl(session)
    user_reader = UserReaderImpl(session)
    uow = SQLAlchemyUoW(session)

    producer = nearest_birthday_reminders_producer(
        queue, GetByInterval(birthday_reader, uow)
    )
    consumer = nearest_birthday_reminders_consumer(
        queue, GetByID(user_reader, uow), bot
    )

    async def on_startup():
        asyncio.create_task(producer)
        asyncio.create_task(consumer)

    async def on_shutdown():
        await session.close()
        await engine.dispose()

    main_router.startup.register(on_startup)
    main_router.shutdown.register(on_shutdown)

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
