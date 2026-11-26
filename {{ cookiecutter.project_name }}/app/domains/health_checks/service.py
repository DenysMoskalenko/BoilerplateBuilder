{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
import asyncio
import logging

{% if cookiecutter.use_otel_observability == "yes" -%}
from opentelemetry.instrumentation.utils import suppress_instrumentation
{% endif -%}
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.health_checks.schemas import LivenessStatus, ReadinessStatus

_logger = logging.getLogger(__name__)


async def check_database_status(session: AsyncSession, timeout_seconds: float) -> LivenessStatus:
    # One line without a traceback, newlines escaped by %r: the kubelet probes every few seconds.
    try:
        async with asyncio.timeout(timeout_seconds):
{%- if cookiecutter.use_otel_observability == "yes" %}
            with suppress_instrumentation():  # no trace per probe, as for the probe's request
                await session.execute(text('SELECT 1'))
{%- else %}
            await session.execute(text('SELECT 1'))
{%- endif %}
    except TimeoutError:
        _logger.warning('Readiness check: the database did not answer within %ss', timeout_seconds)
    except (SQLAlchemyError, OSError) as exc:
        _logger.warning('Readiness check: the database is down: %s: %r', type(exc).__name__, str(exc))
    else:
        return 'UP'
    await session.rollback()
    return 'DOWN'


def resolve_readiness_status(*statuses: LivenessStatus) -> ReadinessStatus:
    if 'DOWN' in statuses:
        return 'NOT_READY'
    return 'READY'
{%- endif %}
