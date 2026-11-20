{%- if cookiecutter.project_type != "fastapi_slim" -%}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import asyncio
{%- endif %}
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, AsyncExitStack
from typing import Any
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from alembic.command import upgrade
{%- endif %}
from fastapi import FastAPI

from app.core.config import get_settings, Settings
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.infrastructure.db.database import async_session_factory, close_database, get_alembic_config
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.infrastructure.llms.provider_bedrock import close_bedrock_client, get_bedrock_client
from app.infrastructure.llms.provider_openai import close_openai_client, get_openai_client
{%- endif %}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    settings = get_settings()
    try:
        await startup(settings)
        yield
    finally:
        await shutdown()


async def startup(settings: Settings) -> None:
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    if settings.MIGRATION_ON_STARTUP:
        alembic_config = get_alembic_config()
        await asyncio.to_thread(upgrade, alembic_config, 'head')
{%- endif %}
    # FastAPI resolves sync dependencies in threads, where concurrent first requests would each build a client.
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    async_session_factory()
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    # By keyword, as FastAPI calls a dependency: lru_cache keys a positional call apart, as another client.
    get_bedrock_client(settings=settings)
    get_openai_client(settings=settings)
{%- endif %}


async def shutdown() -> None:
    async with AsyncExitStack() as clients:  # every client closes even when an earlier one fails to
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
        clients.callback(close_bedrock_client)
        clients.push_async_callback(close_openai_client)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
        clients.push_async_callback(close_database)
{%- endif %}
{%- endif %}
