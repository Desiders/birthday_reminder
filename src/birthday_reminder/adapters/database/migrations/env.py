import asyncio
from logging import getLogger
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from birthday_reminder.adapters.database.models import BaseModel
from birthday_reminder.config import load_config_from_env

logger = getLogger()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata

if not (url := config.get_main_option("sqlalchemy.url")):
    url = load_config_from_env().database.get_postgres_uri()


def run_migrations_offline():
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = AsyncEngine(
        create_engine(
            url=url,
            poolclass=pool.NullPool,
        )
    )

    async with connectable.connect() as connection:
        context.configure(
            connection=connection,  # type: ignore
            target_metadata=target_metadata,
        )

        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
