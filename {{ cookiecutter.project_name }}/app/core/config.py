from functools import lru_cache
{% set is_agent = cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] -%}
{% if is_agent and cookiecutter.use_otel_observability == "yes" -%}
from typing import Literal, Self
{% elif is_agent -%}
from typing import Literal
{% elif cookiecutter.use_otel_observability == "yes" -%}
from typing import Self
{% endif -%}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from pydantic import PostgresDsn
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from pydantic import SecretStr
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}

from pydantic import AnyHttpUrl, Field, model_validator
{%- endif %}
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging import LogFormatType, LogLevel


class Settings(BaseSettings):
    PROJECT_NAME: str = '{{ cookiecutter.project_name }}'
    PROJECT_VERSION: str = '0.1.0'
    LOG_LEVEL: LogLevel = 'INFO'
    LOG_FORMAT: LogFormatType = LogFormatType.STDOUT
    ROOT_PATH: str = ''
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

    DATABASE_URL: PostgresDsn
    MIGRATION_ON_STARTUP: bool = True
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

    AWS_REGION: str = 'eu-central-1'
    AWS_ACCESS_KEY_ID: SecretStr | None = None
    AWS_SECRET_ACCESS_KEY: SecretStr | None = None
    AWS_SESSION_TOKEN: SecretStr | None = None

    OPENAI_API_KEY: SecretStr
    OPENAI_TIMEOUT: int = 180
    OPENAI_BASE_URL: str = ''
    OPENAI_GPT_5_4_MODEL_NAME: str | Literal['gpt-5.4'] = 'gpt-5.4'
    OPENAI_GPT_5_4_MINI_MODEL_NAME: str | Literal['gpt-5.4-mini'] = 'gpt-5.4-mini'
    OPENAI_GPT_5_2_MODEL_NAME: str | Literal['gpt-5.2'] = 'gpt-5.2'
    OPENAI_GPT_5_1_MODEL_NAME: str | Literal['gpt-5.1'] = 'gpt-5.1'

    BEDROCK_CONNECT_TIMEOUT: int = 5
    BEDROCK_READ_TIMEOUT: int = 180
    BEDROCK_CONNECTIONS_POOL_SIZE: int = 30
    BEDROCK_MODEL_SONNET_4_6: str | Literal['eu.anthropic.claude-sonnet-4-6-20260101-v1:0'] = (
        'eu.anthropic.claude-sonnet-4-6-20260101-v1:0'
    )
    BEDROCK_MODEL_OPUS_4_6: str | Literal['eu.anthropic.claude-opus-4-6-20260101-v1:0'] = (
        'eu.anthropic.claude-opus-4-6-20260101-v1:0'
    )
    BEDROCK_MODEL_HAIKU_4_5: str | Literal['eu.anthropic.claude-haiku-4-5-20251001-v1:0'] = (
        'eu.anthropic.claude-haiku-4-5-20251001-v1:0'
    )
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}

    OBSERVABILITY_TRACING_ENABLED: bool = False
    OBSERVABILITY_METRICS_ENABLED: bool = False
    OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT: float = Field(default=100.0, ge=0.0, le=100.0)
    OBSERVABILITY_TRACING_OTLP_ENDPOINT: AnyHttpUrl | None = None

    @model_validator(mode='after')
    def validate_observability_tracing_config(self) -> Self:
        if self.OBSERVABILITY_TRACING_ENABLED and self.OBSERVABILITY_TRACING_OTLP_ENDPOINT is None:
            raise ValueError(
                'OBSERVABILITY_TRACING_OTLP_ENDPOINT is required when OBSERVABILITY_TRACING_ENABLED=True'
            )
        return self
{%- endif %}

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True,
        env_file='.env',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[ty:missing-argument]
