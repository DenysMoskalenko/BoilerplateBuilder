{% if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] -%}
import logging

from fastapi import FastAPI
import uvicorn

{%- if cookiecutter.project_type == "fastapi_db" %}

from app.api.examples.routes import router as examples_router
from app.api.health_checks.routes import router as health_checks_router
from app.core.config import get_settings
from app.core.exception_handlers import include_exception_handlers
from app.core.lifespan import lifespan
{%- else %}

from app.api.health_checks.routes import router as health_checks_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}

from app.observability.bootstrap import setup_observability
from app.observability.logging.config import get_uvicorn_logging_config
{%- endif %}


def create_app() -> FastAPI:
    settings = get_settings()
{%- if cookiecutter.use_otel_observability == "yes" %}
{%- else %}
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
    )
{%- endif %}
    _app = FastAPI(
        title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan, root_path=settings.ROOT_PATH
    )
{%- if cookiecutter.project_type == "fastapi_db" %}
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}
    # Setup observability (logging, tracing, metrics)
    setup_observability(_app, settings)
{%- endif %}

{%- if cookiecutter.project_type == "fastapi_db" %}
    _app.include_router(examples_router)
    _app.include_router(health_checks_router)
{%- else %}
    _app.include_router(health_checks_router)
{%- endif %}
{%- if cookiecutter.project_type == "fastapi_db" %}

    include_exception_handlers(_app)  # Keep this at the end to ensure it wraps all middleware/routers (e.g. CORS).
{%- endif %}
    return _app


app = create_app()

if __name__ == '__main__':
{%- if cookiecutter.use_otel_observability == "yes" %}
    log_config, log_level = get_uvicorn_logging_config()
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, log_config=log_config, log_level=log_level)
{%- else %}
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, log_level=get_settings().LOG_LEVEL.lower())
{%- endif %}
{% elif cookiecutter.project_type == "cli_db" -%}
import asyncio
import logging

from sqlalchemy import func, select

from app.core.config import get_settings
from app.core.database import open_db_session
from app.models.example import ExampleModel
{%- if cookiecutter.use_otel_observability == "yes" %}

from app.observability.bootstrap import setup_observability
from app.observability.logging.config import setup_json_logging
from app.observability.metrics import counters
from app.observability.metrics.primitives.enums import Section
{%- endif %}

async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
    )
{%- if cookiecutter.use_otel_observability == "yes" %}
    if settings.OBSERVABILITY_LOGS_IN_JSON:
        setup_json_logging(settings.LOG_LEVEL)

    # Setup observability (logging, tracing, metrics)
    setup_observability(settings)
{%- endif %}
    print(f'{settings.PROJECT_NAME} with database is ready...')  # noqa: T201

    # Example database usage
    async with open_db_session() as session:
        # You can add your database operations here
        # For example, count records in the example table
        result = await session.execute(select(func.count(ExampleModel.id)))
        count = result.scalar()
        print(f'Found {count} examples in database')  # noqa: T201
{%- if cookiecutter.use_otel_observability == "yes" %}
        counters.database_operations_total.labels(Section.DATABASE_QUERY).inc()
{%- endif %}


if __name__ == '__main__':
    asyncio.run(main())
{% else -%}
import asyncio
import logging

from app.core.config import get_settings
{%- if cookiecutter.use_otel_observability == "yes" %}

from app.observability.bootstrap import setup_observability
from app.observability.logging.config import setup_json_logging
{%- endif %}

async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
    )
{%- if cookiecutter.use_otel_observability == "yes" %}
    if settings.OBSERVABILITY_LOGS_IN_JSON:
        setup_json_logging(settings.LOG_LEVEL)

    # Setup observability (logging, tracing, metrics)
    setup_observability(settings)
{%- endif %}
    print(f'{settings.PROJECT_NAME} is ready...')  # noqa: T201


if __name__ == '__main__':
    asyncio.run(main())
{%- endif %}
