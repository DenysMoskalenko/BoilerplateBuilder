{% if cookiecutter.project_type == "fastapi_db" -%}
from asyncio import DefaultEventLoopPolicy
import os
import pathlib
from typing import Any, AsyncGenerator, AsyncIterable, Generator

from alembic.command import downgrade, upgrade
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.config import get_settings
from tests.dependencies import override_app_test_dependencies, override_dependency

TEST_HOST = 'http://test'


def pytest_configure(config: pytest.Config) -> None:
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    os.environ['MIGRATION_ON_STARTUP'] = 'False'
{%- if cookiecutter.use_otel_observability == "yes" %}
    os.environ['OBSERVABILITY_TRACING_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_METRICS_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_LOGS_IN_JSON'] = 'False'
{%- endif %}


@pytest.fixture(scope='session')
async def app() -> AsyncGenerator[FastAPI, Any]:
    from app.main import create_app

    _app = create_app()
    override_app_test_dependencies(_app)

    yield _app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST) as client:
        yield client


@pytest.fixture(scope='function')
async def session(app: FastAPI, _engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_factory = async_sessionmaker(connection, expire_on_commit=False)
    session = session_factory()

    from app.core.database import get_session

    override_dependency(app, get_session, lambda: session)

    try:
        yield session
    finally:
        await trans.rollback()
        await session.close()
        await connection.close()


@pytest.fixture(scope='session')
async def _engine(_postgres_container: PostgresContainer) -> AsyncIterable[AsyncEngine]:
    settings = get_settings()

    from app.core.database import get_alembic_config

    alembic_config = get_alembic_config(settings.DATABASE_URL, script_location=find_migrations_script_location())

    engine = create_async_engine(settings.DATABASE_URL.unicode_string())
    async with engine.begin() as connection:
        await connection.run_sync(lambda conn: downgrade(alembic_config, 'base'))
        await connection.run_sync(lambda conn: upgrade(alembic_config, 'head'))

    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(lambda conn: downgrade(alembic_config, 'base'))
        await engine.dispose()


@pytest.fixture(scope='session', autouse=True)
def _postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer(
        image='postgres:latest', username='test_boilerplate', password='test_boilerplate', dbname='TestBoilerPlate'
    ) as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        os.environ['DATABASE_URL'] = (
            f'postgresql+psycopg://{postgres.username}:{postgres.password}@{host}:{port}/{postgres.dbname}'
        )
        yield postgres


def find_migrations_script_location() -> str:
    """Help find script location if tests were run by debugger or any other way except writing 'pytest' in cli"""
    return os.path.join(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent, 'migrations')


@pytest.fixture(scope='session', params=(DefaultEventLoopPolicy(),))
def event_loop_policy(request):
    return request.param
{% elif cookiecutter.project_type == "fastapi_slim" -%}
from asyncio import DefaultEventLoopPolicy
import os
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import pytest

from tests.dependencies import override_app_test_dependencies

TEST_HOST = 'http://test'


def pytest_configure(config: pytest.Config) -> None:
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
{%- if cookiecutter.use_otel_observability == "yes" %}
    os.environ['OBSERVABILITY_TRACING_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_METRICS_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_LOGS_IN_JSON'] = 'False'
{%- endif %}


@pytest.fixture(scope='session')
async def app() -> AsyncGenerator[FastAPI, Any]:
    from app.main import create_app

    _app = create_app()
    override_app_test_dependencies(_app)

    yield _app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST) as client:
        yield client


@pytest.fixture(scope='session', params=(DefaultEventLoopPolicy(),))
def event_loop_policy(request):
    return request.param
{% elif cookiecutter.project_type == "cli_db" -%}
from asyncio import DefaultEventLoopPolicy
import os
import pathlib
from typing import Any, AsyncIterable, Generator

from alembic.command import downgrade, upgrade
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.config import get_settings


def pytest_configure(config: pytest.Config) -> None:
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    os.environ['MIGRATION_ON_STARTUP'] = 'False'
{%- if cookiecutter.use_otel_observability == "yes" %}
    os.environ['OBSERVABILITY_TRACING_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_METRICS_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_LOGS_IN_JSON'] = 'False'
{%- endif %}


@pytest.fixture(scope='function')
async def session(_engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_factory = async_sessionmaker(connection, expire_on_commit=False)
    session = session_factory()

    try:
        yield session
    finally:
        await trans.rollback()
        await session.close()
        await connection.close()


@pytest.fixture(scope='session')
async def _engine(_postgres_container: PostgresContainer) -> AsyncIterable[AsyncEngine]:
    settings = get_settings()

    from app.core.database import get_alembic_config

    alembic_config = get_alembic_config(settings.DATABASE_URL, script_location=find_migrations_script_location())

    engine = create_async_engine(settings.DATABASE_URL.unicode_string())
    async with engine.begin() as connection:
        await connection.run_sync(lambda conn: downgrade(alembic_config, 'base'))
        await connection.run_sync(lambda conn: upgrade(alembic_config, 'head'))

    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(lambda conn: downgrade(alembic_config, 'base'))
        await engine.dispose()


@pytest.fixture(scope='session', autouse=True)
def _postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer(
        image='postgres:latest', username='test_boilerplate', password='test_boilerplate', dbname='TestBoilerPlate'
    ) as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        os.environ['DATABASE_URL'] = (
            f'postgresql+psycopg://{postgres.username}:{postgres.password}@{host}:{port}/{postgres.dbname}'
        )
        yield postgres


def find_migrations_script_location() -> str:
    """Help find script location if tests were run by debugger or any other way except writing 'pytest' in cli"""
    return os.path.join(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent, 'migrations')


@pytest.fixture(scope='session', params=(DefaultEventLoopPolicy(),))
def event_loop_policy(request):
    return request.param
{% else -%}
from asyncio import DefaultEventLoopPolicy
import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
{%- if cookiecutter.use_otel_observability == "yes" %}
    os.environ['OBSERVABILITY_TRACING_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_METRICS_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_LOGS_IN_JSON'] = 'False'
{%- endif %}


@pytest.fixture(scope='session', params=(DefaultEventLoopPolicy(),))
def event_loop_policy(request):
    return request.param
{%- endif %}
