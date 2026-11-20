{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from datetime import datetime, UTC

from pydantic import Field, field_validator

from app.infrastructure.db.filters import BaseFilter
from app.infrastructure.db.models.example import ExampleModel


class ExampleFilter(BaseFilter):
    id__in: list[int] | None = None
    search: str | None = Field(default=None, min_length=1, max_length=128)
    created_at__gte: datetime | None = None
    created_at__lte: datetime | None = None
    order_by: list[str] | None = Field(default=['-created_at'])

    class Constants(BaseFilter.Constants):
        model = ExampleModel
        search_model_fields = ['name', 'description']  # noqa: RUF012
        allowed_order_by_fields = ('name', 'description', 'birthday', 'created_at', 'updated_at')

    @field_validator('created_at__gte', 'created_at__lte')
    @classmethod
    def normalize_datetime_filter(cls, value: datetime | None) -> datetime | None:
        if value is None or value.tzinfo is not None:
            return value
        return value.replace(tzinfo=UTC)
{%- endif %}
