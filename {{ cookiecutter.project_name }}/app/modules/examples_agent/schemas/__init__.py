{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from app.modules.examples_agent.schemas.schemas_agent import (
    ExampleAgentDeps,
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    CountExamplesToolInput,
    ExampleAgentToolExample,
    ListExamplesToolInput,
{%- endif %}
)
from app.modules.examples_agent.schemas.schemas_api import ExampleAgentRequest, ExampleAgentResponse

__all__ = [
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    'CountExamplesToolInput',
{%- endif %}
    'ExampleAgentDeps',
    'ExampleAgentRequest',
    'ExampleAgentResponse',
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    'ExampleAgentToolExample',
    'ListExamplesToolInput',
{%- endif %}
]
{%- endif %}
