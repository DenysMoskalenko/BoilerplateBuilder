{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from datetime import date, datetime, UTC
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.schemas import BaseListSorting


class _ExampleBase(BaseModel):
    name: str = Field(min_length=1, max_length=128, examples=['My Example'])
    description: str = Field(min_length=1, max_length=512, examples=['A detailed description of the example'])
    birthday: date | None = Field(default=None, examples=[date(year=1995, month=1, day=1)])


class ExampleCreate(_ExampleBase):
    @field_validator('birthday')
    @classmethod
    def validate_birthday(cls, birthday: date | None) -> date | None:
        if birthday is not None and birthday > datetime.now(UTC).date():
            raise ValueError('Birthday cannot be in the future')
        return birthday


class ExampleUpdate(ExampleCreate):
    pass


class Example(_ExampleBase):
    id: int = Field(description='Example identifier')
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExampleListFilters(BaseModel):
    ids: list[int] | None = Field(default=None, description='Filter by example ids')
    name: str | None = Field(default=None, min_length=1, max_length=128, description='Filter by name')
    description: str | None = Field(default=None, min_length=1, max_length=512, description='Filter by description')
    created_from: datetime | None = Field(default=None, description='Filter by created at lower bound')
    created_to: datetime | None = Field(default=None, description='Filter by created at upper bound')

    @field_validator('created_from', 'created_to')
    @classmethod
    def normalize_datetime_filter(cls, value: datetime | None) -> datetime | None:
        if value is None or value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)


class ExampleListSorting(BaseListSorting):
    sort_by: Literal['name', 'description', 'birthday', 'created_at', 'updated_at'] = Field(
        default='created_at', description='Sorting field'
    )
{%- endif %}
