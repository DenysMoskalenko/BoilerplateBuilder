{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from dataclasses import dataclass
{%- if cookiecutter.project_type == "fastapi_db_agent" %}

from pydantic import BaseModel, Field

from app.api.v1.examples.schemas import ExampleListFilters
from app.services.example_service import ExampleService
{%- endif %}


@dataclass(frozen=True, slots=True)
class ExampleAgentDeps:
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    example_service: ExampleService
{%- else %}
    pass
{%- endif %}
{%- if cookiecutter.project_type == "fastapi_db_agent" %}


class ExampleAgentToolExample(BaseModel):
    id: int
    name: str
    description: str


class CountExamplesToolInput(BaseModel):
    filters: ExampleListFilters = Field(default_factory=ExampleListFilters)


class ListExamplesToolInput(BaseModel):
    filters: ExampleListFilters = Field(default_factory=ExampleListFilters)
    limit: int = Field(default=20, ge=1, le=100)
{%- endif %}
{%- endif %}
