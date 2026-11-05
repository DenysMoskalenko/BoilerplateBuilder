{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from functools import lru_cache
from typing import Annotated

import boto3
from botocore.config import Config
from fastapi import Depends
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from pydantic_ai.providers.bedrock import BedrockProvider

from app.core.config import get_settings, Settings


@lru_cache
def get_bedrock_client(settings: Annotated[Settings, Depends(get_settings)]) -> BedrockRuntimeClient:
    return boto3.client(
        'bedrock-runtime',
        region_name=settings.AWS.region,
        aws_access_key_id=settings.AWS.access_key_id.get_secret_value() if settings.AWS.access_key_id else None,
        aws_secret_access_key=(
            settings.AWS.secret_access_key.get_secret_value() if settings.AWS.secret_access_key else None
        ),
        aws_session_token=settings.AWS.session_token.get_secret_value() if settings.AWS.session_token else None,
        config=Config(
            connect_timeout=settings.BEDROCK.connect_timeout_seconds,
            read_timeout=settings.BEDROCK.read_timeout_seconds,
            max_pool_connections=settings.BEDROCK.connections_pool_size,
        ),
    )


def get_bedrock_provider(
    bedrock_client: Annotated[BedrockRuntimeClient, Depends(get_bedrock_client)],
) -> BedrockProvider:
    return BedrockProvider(bedrock_client=bedrock_client)
{%- endif %}
