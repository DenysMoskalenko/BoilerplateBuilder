{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from enum import StrEnum

from pydantic import BaseModel, Field


class ExampleAgentModelName(StrEnum):
    PRIMARY = 'primary'
    FALLBACK = 'fallback'


class ExampleAgentRequest(BaseModel):
    model: ExampleAgentModelName
    question: str = Field(min_length=1, max_length=2_048)


class ExampleAgentResponse(BaseModel):
    answer: str = Field(min_length=1)
{%- endif %}
