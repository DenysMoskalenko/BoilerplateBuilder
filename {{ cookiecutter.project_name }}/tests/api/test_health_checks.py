{%- if cookiecutter.project_type == "fastapi_db" %}
from datetime import UTC, datetime

from fastapi import FastAPI
from freezegun import freeze_time
from httpx import AsyncClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
from app.core.config import get_settings
from app.core.database import get_session
from tests.dependencies import override_dependency


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_live_success(client: AsyncClient) -> None:
    response = await client.get('/health/live')
    assert response.status_code == 200

    actual = HealthCheckLiveResponse.model_validate(response.json())
    assert actual == HealthCheckLiveResponse(
        version=get_settings().PROJECT_VERSION, status='UP', timestamp=datetime.now(UTC)
    )


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_success(client: AsyncClient, session: AsyncSession) -> None:
    response = await client.get('/health/ready')
    assert response.status_code == 200

    actual = HealthCheckReadyResponse.model_validate(response.json())
    assert actual == HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(database='UP'),
        timestamp=datetime.now(UTC),
    )


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_not_ready(app: FastAPI, client: AsyncClient) -> None:
    class FailingSession:
        async def execute(self, *args, **kwargs):
            raise SQLAlchemyError('db down')

    previous_override = app.dependency_overrides.get(get_session)
    override_dependency(app, get_session, lambda: FailingSession())

    try:
        response = await client.get('/health/ready')
    finally:
        if previous_override is not None:
            override_dependency(app, get_session, previous_override)
    assert response.status_code == 503

    actual = HealthCheckReadyResponse.model_validate(response.json())
    assert actual == HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION,
        status='NOT_READY',
        dependencies=HealthCheckReadyDependencies(database='DOWN'),
        timestamp=datetime.now(UTC),
    )
{%- elif cookiecutter.project_type == "fastapi_slim" %}
from datetime import UTC, datetime

from freezegun import freeze_time
from httpx import AsyncClient

from app.api.health_checks.schemas import HealthCheckLiveResponse, HealthCheckReadyResponse
from app.core.config import get_settings


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_live_success(client: AsyncClient) -> None:
    response = await client.get('/health/live')
    assert response.status_code == 200

    payload = HealthCheckLiveResponse.model_validate(response.json())
    assert payload == HealthCheckLiveResponse(
        version=get_settings().PROJECT_VERSION, status='UP', timestamp=datetime.now(UTC)
    )


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_success(client: AsyncClient) -> None:
    response = await client.get('/health/ready')
    assert response.status_code == 200

    payload = HealthCheckReadyResponse.model_validate(response.json())
    assert payload == HealthCheckReadyResponse(
        version=get_settings().PROJECT_VERSION, status='READY', dependencies={}, timestamp=datetime.now(UTC)
    )
{%- endif %}
