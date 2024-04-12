from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from birthday_reminder.config import Database as DatabaseConfig


def get_engine(config: DatabaseConfig) -> AsyncEngine:
    engine = create_async_engine(
        config.get_postgres_uri(),
        echo=config.echo,
        pool_size=config.pool_size,
    )
    return engine


def get_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    session_factory = async_sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False
    )
    return session_factory
