import asyncio
from logging import getLogger

from aiogram import Bot, Dispatcher, Router
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats
from aiogram_dialog import setup_dialogs
from fluent.runtime import FluentLocalization, FluentResourceLoader

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
    select_language_dialog,
    show_reminders_dialog,
)
from .presentation.handlers import language_router, start_router, stats_router
from .presentation.middlewares import (
    DatabaseMiddleware,
    I18nMiddleware,
    UserMiddleware,
)
from .presentation.scheduler import nearest_birthday_reminders_consumer

logger = getLogger(__name__)

# Check text in `Important`: https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
background_tasks = set()


async def set_bot_commands(bot: Bot):
    cmd_help = BotCommand(
        command="help",
        description="Show menu",
    )
    cmd_language = BotCommand(
        command="language",
        description="Change language",
    )

    # public = []
    private = [cmd_help, cmd_language]

    # await bot.set_my_commands(public, BotCommandScopeAllGroupChats())
    await bot.set_my_commands(private, BotCommandScopeAllPrivateChats())


async def main():
    config = load_config_from_env()
    configure_logging(config.logging)

    logger.debug("Config loaded", extra={"config": config})

    bot = Bot(token=config.bot.token, parse_mode=None)

    main_router = Router(name="main_router")

    main_router.include_router(start_router)
    main_router.include_router(stats_router)
    main_router.include_router(language_router)

    main_router.include_router(create_remind_dialog)
    main_router.include_router(main_menu_dialog)
    main_router.include_router(delete_remind_dialog)
    main_router.include_router(show_reminders_dialog)
    main_router.include_router(select_language_dialog)

    engine = get_engine(config.database)
    pool = get_session_factory(engine)

    i18n_middleware = I18nMiddleware(
        l10ns={
            locale.code: FluentLocalization(
                [locale.code, config.localization.default],
                ["main.ftl"],
                FluentResourceLoader(str(config.localization.path)),
            )
            for locale in config.localization.locales
        },
        default_lang=config.localization.default,
    )

    main_router.message.middleware.register(i18n_middleware)
    main_router.callback_query.middleware.register(i18n_middleware)

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
        command_task = asyncio.create_task(set_bot_commands(bot))
        background_tasks.add(command_task)
        command_task.add_done_callback(background_tasks.discard)

        producer_task = asyncio.create_task(producer)
        background_tasks.add(producer_task)
        producer_task.add_done_callback(background_tasks.discard)

        consumer_task = asyncio.create_task(consumer)
        background_tasks.add(consumer_task)
        consumer_task.add_done_callback(background_tasks.discard)

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

    await dispatcher.start_polling(
        bot, allowed_updates=allowed_updates, config=config
    )


if __name__ == "__main__":
    asyncio.run(main())
