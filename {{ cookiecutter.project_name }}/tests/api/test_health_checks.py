{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import asyncio
{%- endif %}
from datetime import datetime, UTC
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import logging
from types import TracebackType
from typing import Any, cast, Self
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
from app.domains.health_checks.service import _abandoned_probes, check_database_status
from app.infrastructure.db.database import async_session_factory
from tests.dependencies import DepOverride, temporary_overrides


class FailingSession:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> None: ...

    async def execute(self, *args: Any, **kwargs: Any) -> None:
        raise SQLAlchemyError('db down')


class UnanswerableSession(FailingSession):
    """Like psycopg on an unreachable server: the query never answers, its cancellation waits for `released`, then
    fails as the connection drops."""

    def __init__(self) -> None:
        self.started, self.cancelled, self.released = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def execute(self, *args: Any, **kwargs: Any) -> None:
        self.started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            self.cancelled.set()
            await self.released.wait()
            raise SQLAlchemyError('connection lost while cancelling') from None
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


{% if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
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


@freeze_time('2024-01-02T03:04:05Z', real_asyncio=True)
async def test_health_ready_database_down_at_its_deadline_while_the_query_still_cancels(
    app: FastAPI, client: AsyncClient, caplog: pytest.LogCaptureFixture
) -> None:
    session = UnanswerableSession()
    settings = get_settings()
    short_deadline = settings.model_copy(
        update={'DATABASE': settings.DATABASE.model_copy(update={'readiness_timeout_seconds': 0.01})}
    )
    overrides = [
        DepOverride(dependency=async_session_factory, override=lambda: lambda: session),
        DepOverride(dependency=get_settings, override=lambda: short_deadline),
    ]
    try:
        with temporary_overrides(app, overrides):
            async with asyncio.timeout(30):  # guards against a hang only: the cancellation runs until `released`
                response = await client.get('/health/ready')
    finally:
        session.released.set()
    await asyncio.wait(set(_abandoned_probes))

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
    assert [record.levelno for record in caplog.records if record.levelno >= logging.WARNING] == [logging.WARNING]


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
{%- else -%}
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
{%- endif %}
