{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from collections.abc import Iterator
{%- endif %}
import os
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import pathlib
{%- endif %}
from typing import Any, AsyncGenerator
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from typing import cast
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from typing import AsyncIterable, Generator
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from alembic.command import downgrade, upgrade
{%- endif %}
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from pydantic_ai import Agent, models as pydantic_ai_models
{%- endif %}
import pytest
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from app.agents.examples_agent.agents import build_examples_agent, get_examples_agent
from app.agents.examples_agent.schemas import ExampleAgentDeps
from app.api.v1.agents.schemas import ExampleAgentResponse
{%- endif %}
from app.core.config import get_settings
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from tests.mocks.agent_mocks import generate_test_agent
{%- endif %}
from tests.dependencies import override_app_test_dependencies
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from tests.dependencies import override_dependency
{%- endif %}

TEST_HOST = 'http://test'


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    os.environ['MIGRATION_ON_STARTUP'] = 'False'
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    os.environ['OPENAI_API_KEY'] = 'test-openai-key'
    cast(Any, pydantic_ai_models).ALLOW_MODEL_REQUESTS = False
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}
    os.environ['OBSERVABILITY_TRACING_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_METRICS_ENABLED'] = 'False'
    os.environ['OBSERVABILITY_LOGS_IN_JSON'] = 'False'
{%- endif %}


@pytest.fixture(scope='session')
async def app(
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    _engine: AsyncEngine,
{%- endif %}
) -> AsyncGenerator[FastAPI, Any]:
    from app.main import create_app

    _app = create_app()
    override_app_test_dependencies(_app)

    yield _app


@pytest.fixture(scope='session')
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=TEST_HOST) as client:
        yield client
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}


@pytest.fixture(scope='function')
def test_examples_agent(app: FastAPI) -> Iterator[Agent[ExampleAgentDeps, ExampleAgentResponse]]:
    yield from generate_test_agent(app, get_examples_agent, build_examples_agent)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


@pytest.fixture(scope='function')
async def session(app: FastAPI, _engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
    connection = await _engine.connect()
    trans = await connection.begin()

    session_factory = async_sessionmaker(connection, expire_on_commit=False)
    session = session_factory()

    from app.infrastructure.db.database import get_session

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

    from app.infrastructure.db.database import get_alembic_config

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
        image='postgres:18-alpine',
        username='test_boilerplate',
        password='test_boilerplate',  # noqa: S106
        dbname='TestBoilerPlate',
    ) as postgres:
        host = postgres.get_container_host_ip()
        port = postgres.get_exposed_port(5432)
        os.environ['DATABASE_URL'] = (
            f'postgresql+psycopg://{postgres.username}:{postgres.password}@{host}:{port}/{postgres.dbname}'
        )

        from app.core.config import get_settings
        from app.infrastructure.db.database import async_engine, async_session_factory

        get_settings.cache_clear()
        async_engine.cache_clear()
        async_session_factory.cache_clear()

        yield postgres


def find_migrations_script_location() -> str:
    """Help find a script location if tests were run by debugger or any other way except writing 'pytest' in cli"""
    return os.path.join(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent, 'migrations')
{%- endif %}
