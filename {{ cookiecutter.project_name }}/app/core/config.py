{% set is_agent = cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] -%}
{% set is_db = cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] -%}
from functools import {% if is_db %}cached_property, {% endif %}lru_cache
from importlib.metadata import version
{% if is_agent and cookiecutter.use_otel_observability == "yes" -%}
from typing import Annotated, Literal, Self
{% elif is_agent -%}
from typing import Literal
{% elif cookiecutter.use_otel_observability == "yes" -%}
from typing import Annotated, Self
{% endif -%}
{% if is_db -%}
from urllib.parse import quote
{% endif -%}
{%- if is_db %}

from pydantic import PostgresDsn, ValidationError
{%- endif %}
{%- if is_db or is_agent %}

from pydantic import SecretStr
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}

from pydantic import AnyUrl, UrlConstraints, model_validator
{%- endif %}
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging import LogFormatType, LogLevel

{% if cookiecutter.use_otel_observability == "yes" -%}
OtlpEndpoint = Annotated[AnyUrl, UrlConstraints(allowed_schemes=['http', 'https', 'grpc', 'grpcs'], host_required=True)]


{% endif -%}
class _EnvSettings(BaseSettings):
    # Every class receives the whole `.env` as input, so any validation error could print another class's secret.
    model_config = SettingsConfigDict(
        env_file='.env', env_ignore_empty=True, extra='ignore', frozen=True, hide_input_in_errors=True
    )


{% if is_db -%}
class DatabaseSettings(_EnvSettings):
    model_config = SettingsConfigDict(env_prefix='DATABASE_')

    host: str
    port: int = Field(default=5432, ge=1, le=65535)
    user: str
    password: SecretStr
    name: str
    connect_timeout_seconds: int = Field(default=5, ge=1)
    readiness_timeout_seconds: float = Field(default=5.0, gt=0)

    @cached_property
    def url(self) -> PostgresDsn:
        try:
            return PostgresDsn.build(
                scheme='postgresql+psycopg',
                username=quote(self.user, safe=''),
                password=quote(self.password.get_secret_value(), safe=''),
                host=self.host,
                port=self.port,
                path=self.name,
            )
        except ValidationError:  # its message prints the whole URL, password included
            raise ValueError('DATABASE_HOST is not a valid URL host') from None


{% endif -%}
{% if is_agent -%}
class OpenAISettings(_EnvSettings):
    model_config = SettingsConfigDict(env_prefix='OPENAI_')

    api_key: SecretStr
    timeout_seconds: int = Field(default=180, gt=0)
    base_url: str = ''
    model_name: str | Literal['gpt-5.4'] = 'gpt-5.4'


class AwsSettings(_EnvSettings):
    model_config = SettingsConfigDict(env_prefix='AWS_')

    region: str = 'eu-central-1'
    access_key_id: SecretStr | None = None
    secret_access_key: SecretStr | None = None
    session_token: SecretStr | None = None


class BedrockSettings(_EnvSettings):
    model_config = SettingsConfigDict(env_prefix='BEDROCK_')

    connect_timeout_seconds: int = Field(default=5, gt=0)
    read_timeout_seconds: int = Field(default=180, gt=0)
    connections_pool_size: int = Field(default=30, ge=1)
    model_name: str | Literal['eu.anthropic.claude-sonnet-4-6-20260101-v1:0'] = (
        'eu.anthropic.claude-sonnet-4-6-20260101-v1:0'
    )


{% endif -%}
{% if cookiecutter.use_otel_observability == "yes" -%}
class ObservabilitySettings(_EnvSettings):
    model_config = SettingsConfigDict(env_prefix='OBSERVABILITY_')

    tracing_enabled: bool = False
    metrics_enabled: bool = False
    tracing_sample_rate_percent: float = Field(default=100.0, ge=0.0, le=100.0)
    tracing_otlp_endpoint: OtlpEndpoint | None = None

    @model_validator(mode='after')
    def validate_observability_tracing_config(self) -> Self:
        if self.tracing_enabled and self.tracing_otlp_endpoint is None:
            raise ValueError('OBSERVABILITY_TRACING_OTLP_ENDPOINT is required when OBSERVABILITY_TRACING_ENABLED=True')
        return self


{% endif -%}
class Settings(_EnvSettings):
    PROJECT_NAME: str = '{{ cookiecutter.project_name }}'
    PROJECT_VERSION: str = Field(default_factory=lambda: version('{{ cookiecutter.project_name }}'))
    LOG_LEVEL: LogLevel = 'INFO'
    LOG_FORMAT: LogFormatType = LogFormatType.STDOUT
    ROOT_PATH: str = ''
{%- if is_db %}
    MIGRATION_ON_STARTUP: bool = True

    DATABASE: DatabaseSettings = Field(default_factory=DatabaseSettings)
{%- endif %}
{%- if is_agent %}

    OPENAI: OpenAISettings = Field(default_factory=OpenAISettings)
    AWS: AwsSettings = Field(default_factory=AwsSettings)
    BEDROCK: BedrockSettings = Field(default_factory=BedrockSettings)
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}

    OBSERVABILITY: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
{%- endif %}


@lru_cache
def get_settings() -> Settings:
    return Settings()
