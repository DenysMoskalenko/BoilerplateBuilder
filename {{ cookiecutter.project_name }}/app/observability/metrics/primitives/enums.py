{%- if cookiecutter.use_otel_observability == "yes" -%}
from enum import StrEnum


class Section(StrEnum):
    """Enumeration of metric section labels."""
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

    EXAMPLES = 'examples'
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    AGENT = 'agent'
{%- endif %}
{%- if cookiecutter.project_type == "fastapi_slim" %}
    GENERAL = 'general'
{%- endif %}
{%- endif %}
