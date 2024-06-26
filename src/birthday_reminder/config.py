import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from logging import getLogger
from os import environ
from pathlib import Path
from typing import Any, Callable, MutableMapping

import pytz
import structlog

__all__ = [
    "Bot",
    "Reminder",
    "Logging",
    "Database",
    "Config",
    "load_config_from_env",
    "configure_logging",
]

logger = getLogger(__name__)


@dataclass
class Bot:
    token: str


@dataclass
class Reminder:
    hour: int
    tz_raw: str
    tz: pytz.BaseTzInfo = field(init=False)

    def __post_init__(self):
        if not 0 <= self.hour <= 23:
            raise ValueError("Hour must be between 0 and 23")

        try:
            self.tz = pytz.timezone(self.tz_raw)
        except pytz.UnknownTimeZoneError:
            raise ValueError(f"Unknown timezone: {self.tz_raw}")

    def get_datetime(self) -> datetime:
        return datetime.now(tz=self.tz).replace(
            hour=self.hour, minute=0, second=0, microsecond=0
        )


@dataclass
class Media:
    capybara_path: Path


@dataclass
class Logging:
    level: str
    path: Path | None = None
    render_json_logs: bool = False


@dataclass
class Locale:
    code: str
    name: str
    flag: str
    label: str | None = field(init=False, default=None)

    def __post_init__(self):
        self.label = f"{self.flag} {self.name}"

    @staticmethod
    def from_code(code: str) -> "Locale":
        match code:
            case "en":
                return Locale(code, "English", "🇬🇧")
            case "ru":
                return Locale(code, "Русский", "🇷🇺")
            case _:
                raise ValueError(f"Unknown locale code: {code}")


@dataclass
class Localization:
    path: Path
    default: str
    locales: list[Locale] = field(default_factory=list)


@dataclass
class Database:
    host: str
    port: int
    user: str
    password: str
    database: str

    echo: bool = False
    pool_size: int = 10

    def get_postgres_uri(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class Config:
    bot: Bot
    reminder: Reminder
    media: Media
    logging: Logging
    localization: Localization
    database: Database


def load_config_from_env() -> Config:
    raw_path = environ.get("LOGGING_PATH")

    bot = Bot(token=environ["BOT_TOKEN"])
    reminder = Reminder(
        hour=int(environ["REMINDER_HOUR"]), tz_raw=environ["REMINDER_TZ"]
    )
    media = Media(capybara_path=Path(environ["MEDIA_CAPYBARA_PATH"]))
    logging = Logging(
        level=environ.get("LOGGING_LEVEL", "INFO").strip(),
        path=Path(raw_path.strip()) if raw_path else None,
        render_json_logs=environ.get("LOGGING_RENDER_JSON_LOGS", "false")
        .strip()
        .lower()
        == "true",
    )
    localization = Localization(
        path=Path(environ["LOCALIZATION_PATH"].strip()),
        default=environ.get("LOCALIZATION_DEFAULT", "en").strip(),
        locales=[
            Locale.from_code(language_code)
            for language_code in environ.get("LOCALIZATION_LOCALES", "en,ru")
            .strip()
            .split(",")
        ],
    )
    database = Database(
        host=environ["POSTGRES_HOST"].strip(),
        port=int(environ["POSTGRES_PORT"].strip()),
        user=environ["POSTGRES_USER"].strip(),
        password=environ["POSTGRES_PASSWORD"].strip(),
        database=environ["POSTGRES_DB"].strip(),
    )

    return Config(
        bot=bot,
        reminder=reminder,
        media=media,
        logging=logging,
        localization=localization,
        database=database,
    )


def configure_logging(config: Logging) -> None:
    common_processors = (
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=True),
        structlog.contextvars.merge_contextvars,
        structlog.processors.dict_tracebacks,
        structlog.processors.CallsiteParameterAdder(
            (
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            )
        ),
    )
    structlog_processors = (
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    )
    logging_processors = (
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
    )

    logging_console_processors: tuple[
        Callable[
            [Any, str, MutableMapping[str, Any]], MutableMapping[str, Any]
        ],
        structlog.dev.ConsoleRenderer,
    ] | tuple[
        Callable[
            [Any, str, MutableMapping[str, Any]], MutableMapping[str, Any]
        ],
        structlog.processors.JSONRenderer,
    ]
    logging_file_processors: tuple[
        Callable[
            [Any, str, MutableMapping[str, Any]], MutableMapping[str, Any]
        ],
        structlog.dev.ConsoleRenderer,
    ] | tuple[
        Callable[
            [Any, str, MutableMapping[str, Any]], MutableMapping[str, Any]
        ],
        structlog.processors.JSONRenderer,
    ]
    if config.render_json_logs:
        logging_console_processors = (
            *logging_processors,
            structlog.processors.JSONRenderer(json.dumps),
        )
        logging_file_processors = (
            *logging_processors,
            structlog.processors.JSONRenderer(json.dumps),
        )
    else:
        logging_console_processors = (
            *logging_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        )
        logging_file_processors = (
            *logging_processors,
            structlog.dev.ConsoleRenderer(colors=False),
        )

    handler = logging.StreamHandler()
    handler.set_name("default")
    handler.setLevel(config.level)

    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=common_processors,
        processors=logging_console_processors,
    )
    handler.setFormatter(console_formatter)

    handlers: list[logging.Handler] = [handler]
    path = config.path
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)

        path = path / "logs.log" if path.is_dir() else path

        file_handler = logging.FileHandler(path)
        file_handler.set_name("file")
        file_handler.setLevel(config.level)
        file_formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=common_processors,  # type: ignore
            processors=logging_file_processors,
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    logging.basicConfig(handlers=handlers, level=config.level)

    structlog.configure(
        processors=common_processors + structlog_processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,  # type: ignore  # noqa
        cache_logger_on_first_use=True,
    )
