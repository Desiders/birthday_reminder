import json
import logging
from dataclasses import dataclass
from logging import getLogger
from os import environ
from pathlib import Path
from typing import Any, Callable, MutableMapping

import structlog

__all__ = [
    "Bot",
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
class Logging:
    level: str
    path: Path | None = None
    render_json_logs: bool = False


@dataclass
class Database:
    host: str
    port: int
    user: str
    password: str
    database: str

    def get_postgres_uri(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class Config:
    bot: Bot
    logging: Logging
    database: Database


def load_config_from_env() -> Config:
    raw_path = environ.get("LOGGING_PATH")

    bot = Bot(token=environ["BOT_TOKEN"])
    logging = Logging(
        level=environ.get("LOGGING_LEVEL", "INFO").strip(),
        path=Path(raw_path.strip()) if raw_path else None,
        render_json_logs=environ.get("LOGGING_RENDER_JSON_LOGS", "false")
        .strip()
        .lower()
        == "true",
    )
    database = Database(
        host=environ["POSTGRES_HOST"].strip(),
        port=int(environ["POSTGRES_PORT"].strip()),
        user=environ["POSTGRES_USER"].strip(),
        password=environ["POSTGRES_PASSWORD"].strip(),
        database=environ["POSTGRES_DB"].strip(),
    )

    return Config(bot=bot, logging=logging, database=database)


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
