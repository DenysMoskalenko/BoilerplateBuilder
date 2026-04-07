{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from sqlalchemy import ColumnExpressionArgument, func, Select


def apply_contains_filter(query: Select, column: ColumnExpressionArgument[str | None], value: str) -> Select:
    return query.where(func.lower(column).contains(value.lower(), autoescape=True))
{%- endif %}
