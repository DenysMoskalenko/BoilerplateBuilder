{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from openai import AsyncOpenAI
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.config import get_settings, Settings


@lru_cache
def get_openai_client(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.OPENAI.api_key.get_secret_value(),
        timeout=settings.OPENAI.timeout_seconds,
        base_url=settings.OPENAI.base_url or None,
    )


async def close_openai_client() -> None:
    try:
        await get_openai_client(settings=get_settings()).close()  # by keyword, as FastAPI built it
    finally:
        get_openai_client.cache_clear()


def get_openai_provider(openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)]) -> OpenAIProvider:
    return OpenAIProvider(openai_client=openai_client)
{%- endif %}
