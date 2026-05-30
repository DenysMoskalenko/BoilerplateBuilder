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
from app.core.logging import build_logging_config, configure_logging
{%- if cookiecutter.project_type != "fastapi_slim" %}
from app.core.exception_handlers import include_exception_handlers
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.core.lifespan import lifespan
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}
from app.core import observability
{%- endif %}


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
        lifespan=lifespan,
{%- endif %}
        root_path=settings.ROOT_PATH,
    )
{%- if cookiecutter.use_otel_observability == "yes" %}
    observability.setup(app=_app, settings=settings)
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
    settings = get_settings()
    uvicorn.run(
        'app.main:create_app',
        factory=True,
        host='0.0.0.0',  # noqa: S104
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
        log_config=build_logging_config(settings.LOG_LEVEL, settings.LOG_FORMAT),
    )
