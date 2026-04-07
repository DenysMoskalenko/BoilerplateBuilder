{%- if cookiecutter.project_type != "fastapi_slim" %}
import asyncio
{%- endif %}
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from openai import AsyncOpenAI
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from sqlalchemy.ext.asyncio import AsyncSession
{%- endif %}

from app.api.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
{%- if cookiecutter.project_type != "fastapi_slim" %}
from app.api.health_checks.checks import (
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    check_bedrock_status,
    check_openai_status,
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    check_database_status,
{%- endif %}
    resolve_readiness_status,
)
{%- endif %}
from app.core.config import get_settings, Settings
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.infrastructure.db.database import get_session
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.infrastructure.llms.provider_bedrock import get_bedrock_client
from app.infrastructure.llms.provider_openai import get_openai_client
{%- endif %}

router = APIRouter(tags=['Health check'])


@router.get('/health/live')
async def health_check_liveness(settings: Annotated[Settings, Depends(get_settings)]) -> HealthCheckLiveResponse:
    return HealthCheckLiveResponse(version=settings.PROJECT_VERSION, status='UP')


{% if cookiecutter.project_type == "fastapi_slim" -%}
@router.get('/health/ready')
async def health_check_readiness(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    return HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status='READY',
        dependencies=HealthCheckReadyDependencies(),
    )
{%- elif cookiecutter.project_type == "fastapi_db" -%}
@router.get('/health/ready')
async def health_check_readiness(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    db_status = await check_database_status(session)

    ready_response = HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status=resolve_readiness_status(db_status),
        dependencies=HealthCheckReadyDependencies(database=db_status),
    )
    if ready_response.status == 'NOT_READY':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ready_response
{%- elif cookiecutter.project_type == "fastapi_agent" -%}
@router.get('/health/ready')
async def health_check_readiness(
    response: Response,
    bedrock_client: Annotated[BedrockRuntimeClient, Depends(get_bedrock_client)],
    openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    bedrock_status, openai_status = await asyncio.gather(
        check_bedrock_status(bedrock_client, settings.BEDROCK_MODEL_HAIKU_4_5),
        check_openai_status(openai_client),
    )

    ready_response = HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status=resolve_readiness_status(bedrock_status, openai_status),
        dependencies=HealthCheckReadyDependencies(bedrock=bedrock_status, openai=openai_status),
    )
    if ready_response.status == 'NOT_READY':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ready_response
{%- elif cookiecutter.project_type == "fastapi_db_agent" -%}
@router.get('/health/ready')
async def health_check_readiness(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    bedrock_client: Annotated[BedrockRuntimeClient, Depends(get_bedrock_client)],
    openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    db_status, bedrock_status, openai_status = await asyncio.gather(
        check_database_status(session),
        check_bedrock_status(bedrock_client, settings.BEDROCK_MODEL_HAIKU_4_5),
        check_openai_status(openai_client),
    )

    ready_response = HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status=resolve_readiness_status(db_status, bedrock_status, openai_status),
        dependencies=HealthCheckReadyDependencies(database=db_status, bedrock=bedrock_status, openai=openai_status),
    )
    if ready_response.status == 'NOT_READY':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ready_response
{%- endif %}
