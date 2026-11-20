{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
import asyncio
import logging

{% if cookiecutter.use_otel_observability == "yes" -%}
from opentelemetry.instrumentation.utils import suppress_instrumentation
{% endif -%}
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.domains.health_checks.schemas import LivenessStatus, ReadinessStatus

_logger = logging.getLogger(__name__)
# asyncio holds tasks weakly: a probe cut off at its deadline stays here until its cancellation has finished.
_abandoned_probes: set[asyncio.Task[None]] = set()


async def check_database_status(
    session_factory: async_sessionmaker[AsyncSession], timeout_seconds: float
) -> LivenessStatus:
    # A task of its own, waited on rather than awaited: cancelling a query, psycopg first asks the server to cancel it
    # and waits for that, seconds past the deadline when the server is unreachable.
    probe = asyncio.create_task(_select_one(session_factory))
    try:
        await asyncio.wait([probe], timeout=timeout_seconds)
    except asyncio.CancelledError:
        _abandon(probe)
        raise
    # One line without a traceback: the kubelet probes every few seconds.
    if not probe.done():
        _abandon(probe)
        _logger.warning('Readiness check: the database did not answer within %ss', timeout_seconds)
        return 'DOWN'
    try:
        probe.result()
    except (SQLAlchemyError, OSError) as exc:
        _logger.warning('Readiness check: the database is down: %s: %r', type(exc).__name__, str(exc))  # %r: no newlines
        return 'DOWN'
    return 'UP'


def resolve_readiness_status(*statuses: LivenessStatus) -> ReadinessStatus:
    if 'DOWN' in statuses:
        return 'NOT_READY'
    return 'READY'


def _abandon(probe: asyncio.Task[None]) -> None:
    probe.cancel()
    _abandoned_probes.add(probe)
    probe.add_done_callback(_forget)


def _forget(probe: asyncio.Task[None]) -> None:
    _abandoned_probes.discard(probe)
    if not probe.cancelled():
        probe.exception()  # seen: a query failing as it cancels must not log a traceback after its one-line DOWN


async def _select_one(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as session:
{%- if cookiecutter.use_otel_observability == "yes" %}
        with suppress_instrumentation():  # no trace per probe, as for the probe's request
            await session.execute(text('SELECT 1'))
{%- else %}
        await session.execute(text('SELECT 1'))
{%- endif %}
{%- endif %}
