{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from datetime import date, datetime, UTC

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
{%- endif %}
