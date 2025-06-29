from functools import lru_cache

{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}
from pydantic import PostgresDsn
{%- endif %}
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Boilerplate'
{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}

    DATABASE_URL: PostgresDsn
    MIGRATION_ON_STARTUP: bool = True  # True for environments and False for local development
{%- endif %}

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True,
        env_file='.env',
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
