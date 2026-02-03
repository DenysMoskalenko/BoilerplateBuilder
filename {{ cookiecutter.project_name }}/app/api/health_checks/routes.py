{%- if cookiecutter.project_type == "fastapi_db" -%}
import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.health_checks.schemas import (
    HealthCheckLiveResponse,
    HealthCheckReadyDependencies,
    HealthCheckReadyResponse,
)
from app.core.config import get_settings, Settings
from app.core.database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Health check'])


@router.get('/health/live')
async def health_check_liveness(settings: Annotated[Settings, Depends(get_settings)]) -> HealthCheckLiveResponse:
    return HealthCheckLiveResponse(version=settings.PROJECT_VERSION, status='UP')


@router.get('/health/ready')
async def health_check_readiness(
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthCheckReadyResponse:
    try:
        await session.execute(text('SELECT 1'))
    except SQLAlchemyError:
        logger.exception('Database readiness check failed')
        db_status: Literal['DOWN'] = 'DOWN'
    else:
        db_status: Literal['UP'] = 'UP'

    ready_response = HealthCheckReadyResponse(
        version=settings.PROJECT_VERSION,
        status='READY' if db_status == 'UP' else 'NOT_READY',
        dependencies=HealthCheckReadyDependencies(database=db_status),
    )
    if ready_response.status == 'NOT_READY':
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ready_response
{%- elif cookiecutter.project_type == "fastapi_slim" -%}
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.health_checks.schemas import HealthCheckLiveResponse, HealthCheckReadyResponse
from app.core.config import get_settings, Settings

router = APIRouter(tags=['Health check'])


@router.get('/health/live')
async def health_check_liveness(settings: Annotated[Settings, Depends(get_settings)]) -> HealthCheckLiveResponse:
    return HealthCheckLiveResponse(version=settings.PROJECT_VERSION, status='UP')


@router.get('/health/ready')
async def health_check_readiness(settings: Annotated[Settings, Depends(get_settings)]) -> HealthCheckReadyResponse:
    return HealthCheckReadyResponse(version=settings.PROJECT_VERSION, status='READY')
{%- endif %}
