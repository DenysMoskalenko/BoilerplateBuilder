{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from typing import Annotated, TypeAlias

from fastapi import Depends
from pydantic_ai.models import Model
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.bedrock import BedrockProvider
from pydantic_ai.providers.openai import OpenAIProvider

from app.core.config import get_settings, Settings
from app.core.enums import AIModelName
from app.infrastructure.llms.provider_bedrock import get_bedrock_provider
from app.infrastructure.llms.provider_openai import get_openai_provider

ModelRegistry: TypeAlias = dict[AIModelName, Model]


def get_llm_models_registry(
    settings: Annotated[Settings, Depends(get_settings)],
    bedrock_provider: Annotated[BedrockProvider, Depends(get_bedrock_provider)],
    openai_provider: Annotated[OpenAIProvider, Depends(get_openai_provider)],
) -> ModelRegistry:
    registry: ModelRegistry = {
        AIModelName.HAIKU_4_5: BedrockConverseModel(
            provider=bedrock_provider, model_name=settings.BEDROCK.model_haiku_4_5
        ),
        AIModelName.SONNET_4_6: BedrockConverseModel(
            provider=bedrock_provider, model_name=settings.BEDROCK.model_sonnet_4_6
        ),
        AIModelName.OPUS_4_6: BedrockConverseModel(
            provider=bedrock_provider, model_name=settings.BEDROCK.model_opus_4_6
        ),
        AIModelName.GPT_5_1: OpenAIChatModel(provider=openai_provider, model_name=settings.OPENAI.gpt_5_1_model_name),
        AIModelName.GPT_5_2: OpenAIChatModel(provider=openai_provider, model_name=settings.OPENAI.gpt_5_2_model_name),
        AIModelName.GPT_5_4_MINI: OpenAIChatModel(
            provider=openai_provider, model_name=settings.OPENAI.gpt_5_4_mini_model_name
        ),
        AIModelName.GPT_5_4: OpenAIChatModel(provider=openai_provider, model_name=settings.OPENAI.gpt_5_4_model_name),
    }
    return registry
{%- endif %}
