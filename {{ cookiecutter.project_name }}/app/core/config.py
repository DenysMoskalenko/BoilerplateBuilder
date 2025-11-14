from functools import lru_cache
from typing import Literal
{%- if cookiecutter.use_otel_observability == "yes" %}
from urllib.parse import urlparse
{%- endif %}

{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}

from pydantic import PostgresDsn{%- if cookiecutter.use_otel_observability == "yes" %}, Field, field_validator, model_validator{%- endif %}

{%- if cookiecutter.use_otel_observability == "yes" %}
from typing_extensions import Self
{%- endif %}
from pydantic_settings import BaseSettings, SettingsConfigDict
{%- else %}

{%- if cookiecutter.use_otel_observability == "yes" %}
from pydantic import Field, field_validator, model_validator
from typing_extensions import Self
{%- endif %}
from pydantic_settings import BaseSettings, SettingsConfigDict
{%- endif %}


class Settings(BaseSettings):
    PROJECT_NAME: str = '{{ cookiecutter.project_name }}'
    PROJECT_VERSION: str = '0.1.0'
    LOG_LEVEL: Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'] = 'INFO'
{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}

    DATABASE_URL: PostgresDsn
    MIGRATION_ON_STARTUP: bool = True  # True for environments and False for local development
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}

    # Observability
    OBSERVABILITY_LOGS_IN_JSON: bool = True
    OBSERVABILITY_TRACING_ENABLED: bool = True
    OBSERVABILITY_OTLP_GRPC_ENDPOINT: str | None = None
    OBSERVABILITY_METRICS_ENABLED: bool = True
    OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT: int = Field(default=100, ge=0, le=100)
{%- endif %}

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True,
        env_file='.env',
    )
{%- if cookiecutter.use_otel_observability == "yes" %}

    @field_validator('OBSERVABILITY_OTLP_GRPC_ENDPOINT')
    @classmethod
    def _validate_otlp_grpc_endpoint(cls, v: str | None) -> str | None:
        del cls
        """Validate OTLP gRPC endpoint format."""
        if not v:
            return v

        parsed = urlparse(v)
        if parsed.scheme != 'grpc':
            raise ValueError('OTLP_GRPC_ENDPOINT must use the grpc:// scheme.')
        if not parsed.hostname:
            raise ValueError('OTLP_GRPC_ENDPOINT must include a hostname.')
        if not parsed.port:
            raise ValueError('OTLP_GRPC_ENDPOINT must include a port.')
        return v

    @model_validator(mode='after')
    def _validate_tracing_endpoint(self) -> Self:
        """Validate tracing configuration dependencies."""
        if self.OBSERVABILITY_TRACING_ENABLED and not self.OBSERVABILITY_OTLP_GRPC_ENDPOINT:
            raise ValueError(
                'Tracing is enabled (OBSERVABILITY_TRACING_ENABLED=True), but no '
                'OBSERVABILITY_OTLP_GRPC_ENDPOINT is configured. Traces cannot be exported.'
            )
        if self.OBSERVABILITY_TRACING_ENABLED and not self.OBSERVABILITY_LOGS_IN_JSON:
            raise ValueError(
                'Tracing is enabled (OBSERVABILITY_TRACING_ENABLED=True), but '
                'OBSERVABILITY_LOGS_IN_JSON is disabled. Traces cannot be exported due to wrong '
                'logging configuration. Please set OBSERVABILITY_LOGS_IN_JSON=True.'
            )
        return self
{%- endif %}


@lru_cache
def get_settings() -> Settings:
    return Settings()
