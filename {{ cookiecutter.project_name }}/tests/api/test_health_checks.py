{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import asyncio
{%- endif %}
from datetime import datetime, UTC
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import logging
from typing import Any
{%- endif %}

from fastapi import FastAPI
from freezegun import freeze_time
from httpx2 import AsyncClient
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
{%- endif %}

from app.domains.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
from app.core.config import get_settings
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.infrastructure.db.database import get_session
from tests.dependencies import DepOverride, temporary_overrides


class FailingSession:
    async def execute(self, *args: Any, **kwargs: Any) -> None:
        raise SQLAlchemyError('db down')

    async def rollback(self) -> None: ...


class HangingSession(FailingSession):
    async def execute(self, *args: Any, **kwargs: Any) -> None:
        await asyncio.Event().wait()
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
async def test_health_ready_success(app: FastAPI, client: AsyncClient, session: AsyncSession) -> None:
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
    with temporary_overrides(app, [DepOverride(dependency=get_session, override=lambda: FailingSession())]):
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
async def test_health_ready_database_down_at_its_deadline(app: FastAPI, client: AsyncClient) -> None:
    settings = get_settings()
    short_deadline = settings.model_copy(
        update={'DATABASE': settings.DATABASE.model_copy(update={'readiness_timeout_seconds': 0.01})}
    )
    overrides = [
        DepOverride(dependency=get_session, override=lambda: HangingSession()),
        DepOverride(dependency=get_settings, override=lambda: short_deadline),
    ]
    with temporary_overrides(app, overrides):
        async with asyncio.timeout(30):  # guards against a hang only
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
