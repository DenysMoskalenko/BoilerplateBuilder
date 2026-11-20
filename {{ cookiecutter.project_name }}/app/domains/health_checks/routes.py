from typing import Annotated

{% if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
{% else -%}
from fastapi import APIRouter, Depends
{% endif %}
from app.domains.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.domains.health_checks.service import check_database_status, resolve_readiness_status
{%- endif %}
from app.core.config import get_settings, Settings
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.infrastructure.db.database import async_session_factory
{%- endif %}

router = APIRouter(tags=['Health check'])


@router.get('/health/live')
async def health_check_liveness(settings: Annotated[Settings, Depends(get_settings)]) -> HealthCheckLiveResponse:
    return HealthCheckLiveResponse(version=settings.PROJECT_VERSION, status='UP')


{% if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] -%}
# Not Bedrock or OpenAI: every pod shares them, so failing readiness on them would take all pods out of traffic at once.
{% endif -%}
{% if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
@router.get('/health/ready', responses={status.HTTP_503_SERVICE_UNAVAILABLE: {'model': HealthCheckReadyResponse}})
async def health_check_readiness(
    response: Response,
    session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(async_session_factory)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    db_status = await check_database_status(session_factory, settings.DATABASE.readiness_timeout_seconds)

    ready_response = HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status=resolve_readiness_status(db_status),
        dependencies=HealthCheckReadyDependencies(database=db_status),
    )
    if ready_response.status == 'NOT_READY':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ready_response
{%- else -%}
@router.get('/health/ready')
async def health_check_readiness(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    return HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(),
    )
{%- endif %}
