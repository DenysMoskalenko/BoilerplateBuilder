{%- if cookiecutter.project_type != "fastapi_slim" -%}
{%- if cookiecutter.project_type != "fastapi_slim" %}
import asyncio
{%- endif %}
import logging
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import CountTokensInputTypeDef
from openai import AsyncOpenAI, OpenAIError
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

{% if cookiecutter.use_otel_observability == "yes" -%}
from opentelemetry.instrumentation.utils import suppress_instrumentation
{% endif -%}
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
{%- endif %}

from app.domains.health_checks.schemas import LivenessStatus, ReadinessStatus

_logger = logging.getLogger(__name__)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
# asyncio holds tasks weakly: a probe cut off at its deadline stays here until its cancellation has finished.
_abandoned_probes: set[asyncio.Task[None]] = set()


async def check_database_status(
    session_factory: async_sessionmaker[AsyncSession], timeout_seconds: float
) -> LivenessStatus:
    # A task of its own, awaited through a shield: cancelling a query, psycopg first asks the server to cancel it and
    # waits for that, seconds past the deadline when the server is unreachable.
    probe = asyncio.create_task(_select_one(session_factory))
    try:
        async with asyncio.timeout(timeout_seconds):
            await asyncio.shield(probe)
    except asyncio.CancelledError:
        _abandon(probe)
        raise
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        _abandon(probe)
        # One line without a traceback: the kubelet probes every few seconds. %r escapes newlines in the error.
        _logger.warning('Readiness check: the database is down: %s: %r', type(exc).__name__, str(exc))
        return 'DOWN'
    return 'UP'
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}


async def check_bedrock_status(
    bedrock_client: BedrockRuntimeClient, model_id: str, timeout_seconds: float
) -> LivenessStatus:
    input_: CountTokensInputTypeDef = {'converse': {'messages': [{'role': 'user', 'content': [{'text': 'ping'}]}]}}
    try:
        async with asyncio.timeout(timeout_seconds):
            # boto3 cannot be cancelled: past the deadline its thread runs on until botocore's own timeouts end it.
            await asyncio.to_thread(bedrock_client.count_tokens, modelId=model_id, input=input_)
    except (BotoCoreError, ClientError, TimeoutError) as exc:
        _logger.warning('Readiness check: Bedrock is down: %s: %r', type(exc).__name__, str(exc))
        return 'DOWN'
    return 'UP'


async def check_openai_status(openai_client: AsyncOpenAI, timeout_seconds: float) -> LivenessStatus:
    try:
        async with asyncio.timeout(timeout_seconds):
            await openai_client.models.list()
    except (OpenAIError, TimeoutError) as exc:
        _logger.warning('Readiness check: OpenAI is down: %s: %r', type(exc).__name__, str(exc))
        return 'DOWN'
    return 'UP'
{%- endif %}


def resolve_readiness_status(*statuses: LivenessStatus) -> ReadinessStatus:
    if 'DOWN' in statuses:
        return 'NOT_READY'
    return 'READY'
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


def _abandon(probe: asyncio.Task[None]) -> None:
    if not probe.done():
        probe.cancel()
        _abandoned_probes.add(probe)
        probe.add_done_callback(_abandoned_probes.discard)


async def _select_one(session_factory: async_sessionmaker[AsyncSession]) -> None:
    async with session_factory() as session:
{%- if cookiecutter.use_otel_observability == "yes" %}
        with suppress_instrumentation():  # no trace per probe, as for the probe's request
            await session.execute(text('SELECT 1'))
{%- else %}
        await session.execute(text('SELECT 1'))
{%- endif %}
{%- endif %}
{%- endif %}
