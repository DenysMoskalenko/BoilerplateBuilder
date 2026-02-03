{%- if cookiecutter.project_type == "fastapi_db" -%}
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthCheckLiveResponse(BaseModel):
    version: str = Field(description='Version of the application', examples=['1.0.0'])
    status: Literal['UP', 'DOWN'] = Field(description='Health status of the application', examples=['UP'])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthCheckReadyDependencies(BaseModel):
    database: Literal['UP', 'DOWN'] = Field(description='Health status of the database', examples=['UP'])


class HealthCheckReadyResponse(BaseModel):
    version: str = Field(description='Version of the application', examples=['1.0.0'])
    status: Literal['READY', 'NOT_READY'] = Field(description='Health status of the application', examples=['UP'])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dependencies: HealthCheckReadyDependencies = Field(description='Health status of the application dependencies')
{%- elif cookiecutter.project_type == "fastapi_slim" -%}
from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthCheckLiveResponse(BaseModel):
    version: str = Field(description='Version of the application', examples=['1.0.0'])
    status: Literal['UP', 'DOWN'] = Field(description='Health status of the application', examples=['UP'])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthCheckReadyResponse(BaseModel):
    version: str = Field(description='Version of the application', examples=['1.0.0'])
    status: Literal['READY', 'NOT_READY'] = Field(description='Health status of the application', examples=['UP'])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    dependencies: dict[str, Literal['UP', 'DOWN']] = Field(
        default_factory=dict, description='Health status of the application dependencies', examples=[{'database': 'UP'}]
    )
{%- endif %}
