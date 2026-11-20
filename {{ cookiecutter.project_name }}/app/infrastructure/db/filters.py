{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import re

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import field_validator


class BaseFilter(Filter):
    """Project base for list filters built on ``fastapi-filter``.

    Sorting is deny-by-default: the library accepts any attribute of the model, so a filter
    that declares ``order_by`` must list its sortable fields in ``allowed_order_by_fields``.
    ``search`` matches its value literally: the library passes it to ``ILIKE`` unescaped.

    Example:
        class GadgetFilter(BaseFilter):
            name: str | None = None
            order_by: list[str] | None = None

            class Constants(BaseFilter.Constants):
                model = GadgetModel
                allowed_order_by_fields = ('name',)
    """

    class Constants(Filter.Constants):
        allowed_order_by_fields: tuple[str, ...] = ()

    @field_validator('order_by', mode='after', check_fields=False)
    @classmethod
    def _restrict_sortable_fields(cls, value: list[str] | None) -> list[str] | None:
        if not value:
            return value

        allowed = set(getattr(cls.Constants, 'allowed_order_by_fields', ()))
        requested = {name.lstrip('+-') for name in value}
        if forbidden := requested - allowed:
            raise ValueError(f'Sorting by {sorted(forbidden)} is not allowed; sortable fields: {sorted(allowed)}')
        return value

    @field_validator('search', mode='after', check_fields=False)
    @classmethod
    def _escape_search_wildcards(cls, value: str | None) -> str | None:
        if value is None or not hasattr(cls.Constants, 'search_model_fields'):
            return value
        return re.sub(r'([\\%_])', r'\\\1', value)  # backslash is PostgreSQL's default LIKE escape
{%- endif %}
