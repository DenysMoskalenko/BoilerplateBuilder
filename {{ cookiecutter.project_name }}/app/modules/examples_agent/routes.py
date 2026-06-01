{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic_ai import Agent

from app.modules.examples_agent.agents import get_examples_agent
from app.modules.examples_agent.schemas import ExampleAgentDeps, ExampleAgentRequest, ExampleAgentResponse
from app.modules.examples_agent.service import ExampleAgentService

router = APIRouter(tags=['Examples Agent'])


@router.post('/agents/examples/conversations')
async def create_agent_response(
    payload: ExampleAgentRequest,
    service: Annotated[ExampleAgentService, Depends()],
    agent: Annotated[Agent[ExampleAgentDeps, ExampleAgentResponse], Depends(get_examples_agent)],
) -> ExampleAgentResponse:
    answer = await service.answer(payload, agent)
    return answer
{%- endif %}
