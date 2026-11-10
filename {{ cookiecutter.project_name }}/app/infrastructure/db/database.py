{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from collections.abc import AsyncGenerator, AsyncIterable
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from alembic.config import Config
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

POSTGRES_INDEXES_NAMING_CONVENTION = {
    'ix': '%(column_0_label)s_idx',
    'uq': '%(table_name)s_%(column_0_name)s_key',
    'ck': '%(table_name)s_%(constraint_name)s_check',
    'fk': '%(table_name)s_%(column_0_name)s_fkey',
    'pk': '%(table_name)s_pkey',
}


class Base(DeclarativeBase):
    __abstract__ = True
    metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


@lru_cache
def async_engine() -> AsyncEngine:
    database = get_settings().DATABASE
    return create_async_engine(
        database.url.unicode_string(),
        pool_pre_ping=True,
        connect_args={'connect_timeout': database.connect_timeout_seconds},
    )


@lru_cache
def async_session_factory() -> async_sessionmaker:
    return async_sessionmaker(
        bind=async_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


async def get_session() -> AsyncIterable[AsyncSession]:
    """Share a cached session via Depends; the provider owns commit/rollback.

    Ordinary endpoints use scope='function' to finish the transaction before responding.
    Streams consuming the session after the endpoint returns require scope='request';
    writes must commit before streaming starts.
    """
    async with open_db_session() as session:
        yield session


@asynccontextmanager
async def open_db_session() -> AsyncGenerator[AsyncSession, Any]:
    """For usage as a context manager outside FastAPI Depends."""
    factory: async_sessionmaker = async_session_factory()
    session: AsyncSession = factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    else:
        await session.commit()
    finally:
        await session.close()


def get_alembic_config(script_location: str = 'migrations') -> Config:
    alembic_config = Config()
    alembic_config.set_main_option('script_location', script_location)
    return alembic_config
{%- endif %}
