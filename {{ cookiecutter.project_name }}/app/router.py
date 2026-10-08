from fastapi import FastAPI

from app.domains.health_checks.routes import router as health_checks_router
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.domains.examples.routes import router as examples_router
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.domains.examples_agent.routes import router as examples_agent_router
{%- endif %}


# Include into the app directly: every nested APIRouter level keeps another copy of each route and its Depends() tree
def setup_routers(app: FastAPI) -> None:
    app.include_router(health_checks_router)
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    app.include_router(examples_agent_router, prefix='/v1')
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    app.include_router(examples_router, prefix='/v1')
{%- endif %}
