{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from app.api.v1.examples.schemas import Example, ExampleCreate, ExampleUpdate

__all__ = ['Example', 'ExampleCreate', 'ExampleUpdate']
{%- endif %}
