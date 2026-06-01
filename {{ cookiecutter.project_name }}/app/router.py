from fastapi import APIRouter

from app.modules.health_checks.routes import router as health_checks_router
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.modules.examples.routes import router as examples_router
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.modules.examples_agent.routes import router as examples_agent_router
{%- endif %}


def create_router() -> APIRouter:
    router = APIRouter()
    router.include_router(health_checks_router)
{%- if cookiecutter.project_type != "fastapi_slim" %}

    router_v1 = APIRouter(prefix='/v1')
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    router_v1.include_router(examples_agent_router)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    router_v1.include_router(examples_router)
{%- endif %}
    router.include_router(router_v1)
{%- endif %}
    return router
