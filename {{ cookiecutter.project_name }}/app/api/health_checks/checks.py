{%- if cookiecutter.project_type != "fastapi_slim" -%}
{%- if cookiecutter.project_type != "fastapi_slim" %}
import asyncio
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from contextlib import suppress
{%- endif %}
import logging
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import CountTokensInputTypeDef
from openai import AsyncOpenAI
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
{%- endif %}

from app.api.health_checks.schemas import LivenessStatus, ReadinessStatus

_logger = logging.getLogger(__name__)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


async def check_database_status(session: AsyncSession) -> LivenessStatus:
    try:
        await session.execute(text('SELECT 1'))
        return 'UP'
    except Exception as exc:
        _logger.error('Database readiness check failed', exc_info=exc)
        with suppress(Exception):
            await session.rollback()
        return 'DOWN'
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}


async def check_bedrock_status(bedrock_client: BedrockRuntimeClient, model_id: str) -> LivenessStatus:
    input_: CountTokensInputTypeDef = {'converse': {'messages': [{'role': 'user', 'content': [{'text': 'ping'}]}]}}
    try:
        await asyncio.to_thread(bedrock_client.count_tokens, modelId=model_id, input=input_)
    except Exception as exc:
        _logger.error('Bedrock health check failed', exc_info=exc)
        return 'DOWN'
    return 'UP'


async def check_openai_status(openai_client: AsyncOpenAI) -> LivenessStatus:
    try:
        await openai_client.models.list()
    except Exception as exc:
        _logger.error('OpenAI health check failed', exc_info=exc)
        return 'DOWN'
    return 'UP'
{%- endif %}


def resolve_readiness_status(*statuses: LivenessStatus) -> ReadinessStatus:
    if 'DOWN' in statuses:
        return 'NOT_READY'
    return 'READY'
{%- endif %}
