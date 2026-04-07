{%- if cookiecutter.project_type != "fastapi_slim" -%}
from fastapi import APIRouter
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from app.api.v1.examples.routes import router as examples_router
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from app.api.v1.agents.routes import router as agents_router
{%- endif %}

router = APIRouter(prefix='/v1')
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
router.include_router(agents_router)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
router.include_router(examples_router)
{%- endif %}
{%- endif %}
