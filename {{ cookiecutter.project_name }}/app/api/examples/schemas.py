{%- if cookiecutter.project_type == "fastapi_db" %}
from datetime import date, datetime, UTC

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExampleCreate(BaseModel):
    name: str = Field(max_length=32)
    birthday: date | None = None

    @field_validator('birthday')
    def validate_start_date(cls, birthday: date | None) -> date | None:
        if birthday is None:
            return birthday
        if birthday < datetime.now(UTC).date():
            return birthday
        raise ValueError('You cannot be born in the future')

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'name': 'John',
                'birthday': '1995-01-01',
            },
        },
    )


class ExampleUpdate(ExampleCreate):
    pass


class Example(BaseModel):
    id: int
    name: str
    birthday: date | None = None

    model_config = ConfigDict(from_attributes=True)
{%- endif %} 