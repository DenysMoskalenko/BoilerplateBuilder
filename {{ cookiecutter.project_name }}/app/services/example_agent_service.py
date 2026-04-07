{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] -%}
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from typing import Annotated

from fastapi import Depends
{%- endif %}
from pydantic_ai import Agent

from app.agents.examples_agent.schemas import ExampleAgentDeps
from app.api.v1.agents.schemas import ExampleAgentRequest, ExampleAgentResponse
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from app.services.example_service import ExampleService
{%- endif %}
{%- if cookiecutter.use_otel_observability == "yes" %}
from app.observability.metrics import counters, gauges
from app.observability.metrics.primitives import increment_after, track_inflight
{%- endif %}


class ExampleAgentService:
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    def __init__(
        self,
        example_service: Annotated[ExampleService, Depends()],
    ) -> None:
        self._example_service = example_service
{%- endif %}

{%- if cookiecutter.use_otel_observability == "yes" %}
    @track_inflight(gauges.agent_inflight_requests)
    @increment_after(counters.agent_requests_total, success_only=False)
{%- endif %}
    async def answer(
        self,
        payload: ExampleAgentRequest,
        agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
    ) -> ExampleAgentResponse:
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
        deps = ExampleAgentDeps(example_service=self._example_service)
{%- else %}
        deps = ExampleAgentDeps()
{%- endif %}
        result = await agent.run(payload.question, deps=deps)
        return result.output
{%- endif %}
