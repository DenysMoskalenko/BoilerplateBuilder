{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import asyncio
{%- endif %}
from datetime import datetime, UTC
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import logging
from types import TracebackType
{%- endif %}
{%- if cookiecutter.project_type != "fastapi_slim" %}
from types import SimpleNamespace
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from typing import Any, cast, Self
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from unittest.mock import AsyncMock
{%- endif %}

from fastapi import FastAPI
from freezegun import freeze_time
from httpx2 import AsyncClient
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
{%- endif %}

from app.domains.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
from app.core.config import get_settings
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.domains.health_checks.service import check_database_status
from app.infrastructure.db.database import async_session_factory
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.infrastructure.llms.provider_bedrock import get_bedrock_client
from app.infrastructure.llms.provider_openai import get_openai_client
{%- endif %}
from tests.dependencies import DepOverride, temporary_overrides
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


class FailingSession:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None: ...

    async def execute(self, *args: Any, **kwargs: Any) -> None:
        raise SQLAlchemyError('db down')


class UnanswerableSession(FailingSession):
    """Like psycopg on an unreachable server: the query never answers, and its cancellation waits for `released`."""

    def __init__(self) -> None:
        self.started, self.cancelled, self.released = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def execute(self, *args: Any, **kwargs: Any) -> None:
        self.started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            self.cancelled.set()
            await self.released.wait()
            raise
{%- endif %}


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_live_success(client: AsyncClient) -> None:
    response = await client.get('/health/live')
    assert response.status_code == 200

    actual = response.json()
    assert HealthCheckLiveResponse.model_validate(actual)
    expected = HealthCheckLiveResponse(
        version=get_settings().PROJECT_VERSION, status='UP', timestamp=datetime.now(UTC)
    ).model_dump(mode='json')
    assert actual == expected


{% if cookiecutter.project_type == "fastapi_slim" -%}
@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_success(app: FastAPI, client: AsyncClient) -> None:
    response = await client.get('/health/ready')

    assert response.status_code == 200

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected
{%- elif cookiecutter.project_type == "fastapi_db" -%}
@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_success(app: FastAPI, client: AsyncClient) -> None:
    response = await client.get('/health/ready')

    assert response.status_code == 200

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(database='UP'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_database_down(app: FastAPI, client: AsyncClient, caplog: pytest.LogCaptureFixture) -> None:
    with temporary_overrides(
        app,
        [DepOverride(dependency=async_session_factory, override=lambda: FailingSession)],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(database='DOWN'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected
    records = [record for record in caplog.records if record.name == 'app.domains.health_checks.service']
    assert [(record.levelno, record.exc_info) for record in records] == [(logging.WARNING, None)]
{%- elif cookiecutter.project_type == "fastapi_agent" -%}
@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_success(app: FastAPI, client: AsyncClient) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 200

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(bedrock='UP', openai='UP'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_bedrock_down(app: FastAPI, client: AsyncClient) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: (_ for _ in ()).throw(RuntimeError('bedrock down')))
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(bedrock='DOWN', openai='UP'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_openai_down(app: FastAPI, client: AsyncClient) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(side_effect=RuntimeError('openai down'))))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(bedrock='UP', openai='DOWN'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected
{%- elif cookiecutter.project_type == "fastapi_db_agent" -%}
@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_success(app: FastAPI, client: AsyncClient) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 200

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(database='UP', bedrock='UP', openai='UP'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_database_down(app: FastAPI, client: AsyncClient, caplog: pytest.LogCaptureFixture) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
            DepOverride(dependency=async_session_factory, override=lambda: FailingSession),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(database='DOWN', bedrock='UP', openai='UP'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected
    records = [record for record in caplog.records if record.name == 'app.domains.health_checks.service']
    assert [(record.levelno, record.exc_info) for record in records] == [(logging.WARNING, None)]


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_bedrock_down(app: FastAPI, client: AsyncClient) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: (_ for _ in ()).throw(RuntimeError('bedrock down')))
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(database='UP', bedrock='DOWN', openai='UP'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_openai_down(app: FastAPI, client: AsyncClient) -> None:
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(side_effect=RuntimeError('openai down'))))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
        ],
    ):
        response = await client.get('/health/ready')

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(database='UP', bedrock='UP', openai='DOWN'),
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_database_down_at_its_deadline_while_the_query_still_cancels(
    app: FastAPI, client: AsyncClient
) -> None:
    session = UnanswerableSession()
    settings = get_settings()
    short_deadline = settings.model_copy(
        update={'DATABASE': settings.DATABASE.model_copy(update={'readiness_timeout_seconds': 0.01})}
    )
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))
{%- endif %}
    overrides = [
        DepOverride(dependency=async_session_factory, override=lambda: lambda: session),
        DepOverride(dependency=get_settings, override=lambda: short_deadline),
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
        DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
        DepOverride(dependency=get_openai_client, override=lambda: openai_client),
{%- endif %}
    ]
    try:
        with temporary_overrides(app, overrides):
            async with asyncio.timeout(30):  # guards against a hang only: the cancellation runs until `released`
                response = await client.get('/health/ready')
    finally:
        session.released.set()

    assert response.status_code == 503

    actual = response.json()
    assert HealthCheckReadyResponse.model_validate(actual)
    expected = HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
        dependencies=HealthCheckReadyDependencies(database='DOWN', bedrock='UP', openai='UP'),
{%- else %}
        dependencies=HealthCheckReadyDependencies(database='DOWN'),
{%- endif %}
        timestamp=datetime.now(UTC),
    ).model_dump(mode='json')
    assert actual == expected


async def test_a_cancelled_readiness_check_cancels_its_query() -> None:
    """A probe cancelled with its request, the client gone, leaves no query behind."""
    session = UnanswerableSession()
    session.released.set()
    check = asyncio.create_task(
        check_database_status(cast(async_sessionmaker[AsyncSession], lambda: session), timeout_seconds=60)
    )

    async with asyncio.timeout(30):  # guards against a hang only
        await session.started.wait()
        check.cancel()
        with pytest.raises(asyncio.CancelledError):
            await check
        await session.cancelled.wait()
{%- endif %}
