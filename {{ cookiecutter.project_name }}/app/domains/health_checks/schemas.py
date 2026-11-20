from datetime import datetime, UTC
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field

LivenessStatus: TypeAlias = Literal['UP', 'DOWN']
ReadinessStatus: TypeAlias = Literal['READY', 'NOT_READY']


class HealthCheckLiveResponse(BaseModel):
    version: str
    status: LivenessStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class HealthCheckReadyDependencies(BaseModel):
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    database: LivenessStatus
{%- else %}
    pass
{%- endif %}


class HealthCheckReadyResponse(BaseModel):
    version: str
    status: ReadinessStatus
    dependencies: HealthCheckReadyDependencies
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
