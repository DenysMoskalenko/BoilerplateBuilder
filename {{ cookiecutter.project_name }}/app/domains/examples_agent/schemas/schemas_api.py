{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from pydantic import BaseModel, Field

from app.core.enums import AIModelName


class ExampleAgentRequest(BaseModel):
    model: AIModelName
    question: str = Field(min_length=1, max_length=2_048)


class ExampleAgentResponse(BaseModel):
    answer: str = Field(min_length=1)
{%- endif %}
