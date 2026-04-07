{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from collections.abc import Sequence
{%- endif %}
from typing import Annotated

from fastapi import Depends
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from fastapi_pagination import Params
{%- endif %}
from pydantic_ai import Agent, ModelSettings, RunContext
from pydantic_ai.models import Model
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings

from app.agents.examples_agent.prompts import EXAMPLE_AGENT_SYSTEM_PROMPT
from app.agents.examples_agent.schemas import (
    ExampleAgentDeps,
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    CountExamplesToolInput,
    ExampleAgentToolExample,
    ListExamplesToolInput,
{%- endif %}
)
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from app.api.v1.examples.schemas import Example, ExampleListSorting
{%- endif %}
from app.api.v1.agents.schemas import ExampleAgentRequest, ExampleAgentResponse
from app.infrastructure.llms.llm_models import get_llm_models_registry, ModelRegistry


def get_examples_agent(
    payload: ExampleAgentRequest,
    model_registry: Annotated[ModelRegistry, Depends(get_llm_models_registry)],
) -> Agent[ExampleAgentDeps, ExampleAgentResponse]:
    """The FastAPI Dependency for getting examples agent"""
    return build_examples_agent(model_registry[payload.model])


def build_examples_agent(model: Model) -> Agent[ExampleAgentDeps, ExampleAgentResponse]:
    agent = Agent[ExampleAgentDeps, ExampleAgentResponse](
        model=model,
        output_type=ExampleAgentResponse,
        deps_type=ExampleAgentDeps,
        system_prompt=EXAMPLE_AGENT_SYSTEM_PROMPT,
        retries=0,
        model_settings=_get_examples_agent_model_settings(model),
    )
    # Add agent tools here
{%- if cookiecutter.project_type == "fastapi_db_agent" %}

    @agent.tool
    async def count_examples(ctx: RunContext[ExampleAgentDeps], payload: CountExamplesToolInput) -> int:
        return await ctx.deps.example_service.count_examples(payload.filters)

    @agent.tool
    async def list_examples(
        ctx: RunContext[ExampleAgentDeps], payload: ListExamplesToolInput
    ) -> list[ExampleAgentToolExample]:
        examples_page = await ctx.deps.example_service.list_examples(
            payload.filters,
            ExampleListSorting(sort_by='name', sort_order='asc'),
            pagination_params=Params(page=1, size=payload.limit),
        )
        return _build_tool_examples(examples_page.items)
{%- endif %}

    return agent


def _get_examples_agent_model_settings(model: Model) -> ModelSettings:
    settings = ModelSettings(max_tokens=2048, temperature=0.7)
    if isinstance(model, BedrockConverseModel):
        return BedrockModelSettings(**settings, bedrock_cache_instructions=True, bedrock_cache_tool_definitions=True)
    return settings
{%- if cookiecutter.project_type == "fastapi_db_agent" %}


def _build_tool_examples(examples: Sequence[Example]) -> list[ExampleAgentToolExample]:
    return [
        ExampleAgentToolExample(
            id=example.id,
            name=example.name,
            description=example.description,
        )
        for example in examples
    ]
{%- endif %}
{%- endif %}
