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
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        timeout=settings.OPENAI_TIMEOUT,
        base_url=settings.OPENAI_BASE_URL or None,
    )


def get_openai_provider(openai_client: Annotated[AsyncOpenAI, Depends(get_openai_client)]) -> OpenAIProvider:
    return OpenAIProvider(openai_client=openai_client)
{%- endif %}
