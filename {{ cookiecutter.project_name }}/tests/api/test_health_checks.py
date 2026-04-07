from datetime import datetime, UTC
{%- if cookiecutter.project_type != "fastapi_slim" %}
from types import SimpleNamespace
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from typing import Any, Never
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from unittest.mock import AsyncMock
{%- endif %}

from fastapi import FastAPI
from freezegun import freeze_time
from httpx import AsyncClient
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
{%- endif %}

from app.api.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
from app.core.config import get_settings
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.infrastructure.db.database import get_session
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.infrastructure.llms.provider_bedrock import get_bedrock_client
from app.infrastructure.llms.provider_openai import get_openai_client
{%- endif %}
from tests.dependencies import DepOverride, temporary_overrides


@freeze_time('2024-01-02T03:04:05Z')
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
@freeze_time('2024-01-02T03:04:05Z')
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
@freeze_time('2024-01-02T03:04:05Z')
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


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_database_down(app: FastAPI, client: AsyncClient) -> None:
    class FailingSession:
        async def execute(self, *args: Any, **kwargs: Any) -> Never:
            raise SQLAlchemyError('db down')

    with temporary_overrides(
        app,
        [DepOverride(dependency=get_session, override=lambda: FailingSession())],
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
{%- elif cookiecutter.project_type == "fastapi_agent" -%}
@freeze_time('2024-01-02T03:04:05Z')
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


@freeze_time('2024-01-02T03:04:05Z')
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


@freeze_time('2024-01-02T03:04:05Z')
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
@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_success(app: FastAPI, client: AsyncClient, session: AsyncSession) -> None:
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


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_database_down(app: FastAPI, client: AsyncClient) -> None:
    class FailingSession:
        async def execute(self, *args: Any, **kwargs: Any) -> Never:
            raise SQLAlchemyError('db down')

    bedrock_client = SimpleNamespace(count_tokens=lambda **kwargs: {'inputTokens': 1})
    openai_client = SimpleNamespace(models=SimpleNamespace(list=AsyncMock(return_value=None)))

    with temporary_overrides(
        app,
        [
            DepOverride(dependency=get_bedrock_client, override=lambda: bedrock_client),
            DepOverride(dependency=get_openai_client, override=lambda: openai_client),
            DepOverride(dependency=get_session, override=lambda: FailingSession()),
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


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_bedrock_down(app: FastAPI, client: AsyncClient, session: AsyncSession) -> None:
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


@freeze_time('2024-01-02T03:04:05Z')
async def test_health_ready_openai_down(app: FastAPI, client: AsyncClient, session: AsyncSession) -> None:
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
