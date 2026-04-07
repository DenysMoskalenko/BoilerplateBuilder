{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from alembic.command import upgrade
from fastapi import FastAPI

from app.core.config import get_settings, Settings
from app.infrastructure.db.database import get_alembic_config


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, Any]:
    settings = get_settings()
    await startup(settings)
    yield
    await shutdown()


async def startup(settings: Settings) -> None:
    if settings.MIGRATION_ON_STARTUP:
        alembic_config = get_alembic_config(settings.DATABASE_URL)
        await asyncio.to_thread(upgrade, alembic_config, 'head')


async def shutdown() -> None: ...
{%- endif %}
