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
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID.get_secret_value() if settings.AWS_ACCESS_KEY_ID else None,
        aws_secret_access_key=(
            settings.AWS_SECRET_ACCESS_KEY.get_secret_value() if settings.AWS_SECRET_ACCESS_KEY else None
        ),
        aws_session_token=settings.AWS_SESSION_TOKEN.get_secret_value() if settings.AWS_SESSION_TOKEN else None,
        config=Config(
            connect_timeout=settings.BEDROCK_CONNECT_TIMEOUT,
            read_timeout=settings.BEDROCK_READ_TIMEOUT,
            max_pool_connections=settings.BEDROCK_CONNECTIONS_POOL_SIZE,
        ),
    )


def get_bedrock_provider(
    bedrock_client: Annotated[BedrockRuntimeClient, Depends(get_bedrock_client)],
) -> BedrockProvider:
    return BedrockProvider(bedrock_client=bedrock_client)
{%- endif %}
