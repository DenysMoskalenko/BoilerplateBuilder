{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from typing import Annotated

from fastapi import Depends
from pydantic_ai.models import Model
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.config import get_settings, Settings
from app.infrastructure.llms.provider_bedrock import get_bedrock_provider
from app.infrastructure.llms.provider_openai import get_openai_provider


def get_primary_model(
    settings: Annotated[Settings, Depends(get_settings)],
    openai_provider: Annotated[OpenAIProvider, Depends(get_openai_provider)],
) -> Model:
    return OpenAIChatModel(provider=openai_provider, model_name=settings.OPENAI.model_name)


def get_fallback_model(
    settings: Annotated[Settings, Depends(get_settings)],
    bedrock_provider: Annotated[BedrockProvider, Depends(get_bedrock_provider)],
) -> Model:
    return BedrockConverseModel(provider=bedrock_provider, model_name=settings.BEDROCK.model_name)
{%- endif %}
