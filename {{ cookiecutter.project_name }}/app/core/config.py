from functools import lru_cache
from typing import Literal
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from pydantic import PostgresDsn
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from pydantic import SecretStr
{%- endif %}
from pydantic_settings import BaseSettings, SettingsConfigDict
{%- if cookiecutter.use_otel_observability == "yes" %}

from pydantic import field_validator, model_validator
{%- endif %}


class Settings(BaseSettings):
    PROJECT_NAME: str = '{{ cookiecutter.project_name }}'
    PROJECT_VERSION: str = '0.1.0'
    LOG_LEVEL: Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'] = 'INFO'
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

    OBSERVABILITY_LOGS_IN_JSON: bool = True
    OBSERVABILITY_TRACING_ENABLED: bool = True
    OBSERVABILITY_OTLP_GRPC_ENDPOINT: str = ''
    OBSERVABILITY_METRICS_ENABLED: bool = True
    OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT: int = 100

    @field_validator('OBSERVABILITY_OTLP_GRPC_ENDPOINT')
    @classmethod
    def validate_otlp_endpoint(cls, value: str) -> str:
        if not value:
            return value
        if not value.startswith('grpc://'):
            raise ValueError('OTLP_GRPC_ENDPOINT must use the grpc:// scheme')
        rest = value[len('grpc://'):]
        if not rest or rest.startswith(':'):
            raise ValueError('OTLP_GRPC_ENDPOINT must include a hostname')
        if ':' not in rest:
            raise ValueError('OTLP_GRPC_ENDPOINT must include a port')
        return value

    @field_validator('OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT')
    @classmethod
    def validate_sample_rate(cls, value: int) -> int:
        if not 0 <= value <= 100:
            raise ValueError('OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT must be between 0 and 100')
        return value

    @model_validator(mode='after')
    def validate_tracing_requires_endpoint(self) -> 'Settings':
        if self.OBSERVABILITY_TRACING_ENABLED and not self.OBSERVABILITY_OTLP_GRPC_ENDPOINT:
            raise ValueError(
                'Tracing is enabled but no OBSERVABILITY_OTLP_GRPC_ENDPOINT is configured'
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
