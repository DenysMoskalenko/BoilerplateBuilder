{%- if cookiecutter.project_type != "fastapi_slim" %}
from fastapi import FastAPI

{% if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] -%}
from app.core.config import get_settings
{% endif -%}
from app.core.lifespan import shutdown
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.infrastructure.db.database import async_engine, async_session_factory
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.infrastructure.llms.provider_bedrock import get_bedrock_client
from app.infrastructure.llms.provider_openai import get_openai_client
{%- endif %}

CLIENT_GETTERS = (
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    async_session_factory,
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    get_bedrock_client,
    get_openai_client,
{%- endif %}
)


async def test_lifespan_builds_the_clients_at_startup_and_closes_them_at_shutdown(app: FastAPI) -> None:
    """Startup builds each client once: FastAPI runs sync dependencies in threads, where first requests would race."""
    await shutdown()  # closes what earlier tests opened
    async with app.router.lifespan_context(app):
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
        # As a request gets them: FastAPI calls a dependency with keyword arguments.
        get_bedrock_client(settings=get_settings())
        openai_client = get_openai_client(settings=get_settings())
{%- endif %}
        clients = [getter.cache_info().currsize for getter in CLIENT_GETTERS]
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
        async with async_engine().connect() as connection:
            pooled_connection = (await connection.get_raw_connection()).driver_connection
{%- endif %}

    assert clients == [1] * len(CLIENT_GETTERS)
    assert [getter.cache_info().currsize for getter in CLIENT_GETTERS] == [0] * len(CLIENT_GETTERS)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    assert pooled_connection is not None and pooled_connection.closed
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    assert openai_client.is_closed()
{%- endif %}
{%- endif %}
