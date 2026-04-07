{%- if cookiecutter.use_otel_observability != "yes" %}
import logging
{%- endif %}

from fastapi import FastAPI
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from fastapi_pagination import add_pagination
{%- endif %}
import uvicorn
{%- if cookiecutter.project_type != "fastapi_slim" %}

from app.api.v1.router import router as v1_router
{%- endif %}
from app.api.health_checks.routes import router as health_checks_router
from app.core.config import get_settings
{%- if cookiecutter.project_type != "fastapi_slim" %}
from app.core.exception_handlers import include_exception_handlers
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.core.lifespan import lifespan
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}
from app.observability.bootstrap import setup_observability
from app.observability.logging.config import get_uvicorn_logging_config
{%- endif %}


def create_app() -> FastAPI:
    settings = get_settings()
{%- if cookiecutter.use_otel_observability != "yes" %}
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
    )
{%- endif %}

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
        lifespan=lifespan,
{%- endif %}
        root_path=settings.ROOT_PATH,
    )
{%- if cookiecutter.use_otel_observability == "yes" %}
    setup_observability(_app, settings)
{%- endif %}
{%- if cookiecutter.project_type != "fastapi_slim" %}
    _app.include_router(v1_router)
{%- endif %}
    _app.include_router(health_checks_router)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    add_pagination(_app)
{%- endif %}
{%- if cookiecutter.project_type != "fastapi_slim" %}

    # Exception handlers must be registered last, after all routers and middleware
    include_exception_handlers(_app)
{%- endif %}
    return _app


if __name__ == '__main__':
{%- if cookiecutter.use_otel_observability == "yes" %}
    log_config, log_level = get_uvicorn_logging_config()
    uvicorn.run(
        'app.main:create_app', factory=True, host='localhost', port=8000,
        log_config=log_config, log_level=log_level,
    )
{%- else %}
    uvicorn.run(
        'app.main:create_app', factory=True, host='localhost', port=8000,
        log_level=get_settings().LOG_LEVEL.lower(),
    )
{%- endif %}
