{%- if cookiecutter.use_otel_observability == "yes" %}
{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}
from enum import StrEnum


class Section(StrEnum):
    """Enumeration of metric section labels."""

{%- if cookiecutter.project_type == "fastapi_db" %}
    CREATE_EXAMPLE = 'create_example'
    UPDATE_EXAMPLE = 'update_example'
    DELETE_EXAMPLE = 'delete_example'
    LIST_EXAMPLES = 'list_examples'
    GET_EXAMPLE = 'get_example'
{%- elif cookiecutter.project_type == "cli_db" %}
    DATABASE_QUERY = 'database_query'
    DATABASE_INSERT = 'database_insert'
    DATABASE_UPDATE = 'database_update'
{%- endif %}
{%- endif %}
{%- endif %}
