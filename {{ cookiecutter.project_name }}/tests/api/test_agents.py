{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
import asyncio
{%- endif %}
import logging

from botocore.exceptions import ReadTimeoutError
from httpx2 import AsyncClient
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError, UsageLimitExceeded
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
{%- endif %}
import pytest
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from sqlalchemy.ext.asyncio import AsyncSession
{%- endif %}

from app.core.enums import AIModelName
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from app.domains.examples.service import ExampleService
{%- endif %}
from app.domains.examples_agent.schemas import ExampleAgentDeps, ExampleAgentResponse
from tests.mocks.agent_mocks import build_mock_model, build_raising_model
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from tests.mocks.agent_mocks import build_output_model_response
{%- endif %}

RATE_LIMITED_DETAIL = 'Too many requests to the AI provider. Please try again in a moment.'
UNAVAILABLE_DETAIL = 'AI provider temporarily unavailable. Please retry shortly.'


class TestCreateExampleAgentResponse:
    @pytest.mark.parametrize('model_name', list(AIModelName))
    async def test_success(
        self,
        client: AsyncClient,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
        model_name: AIModelName,
    ) -> None:
        answer = 'We have 3 examples.'
        with test_examples_agent.override(model=build_mock_model(ExampleAgentResponse(answer=answer))):
            response = await client.post(
                '/v1/agents/examples/conversations',
                json={'model': model_name, 'question': 'How many examples do we have?'},
            )

        assert response.status_code == 200
        assert response.json() == {'answer': answer}

    @pytest.mark.parametrize(
        ('exc', 'expected_status', 'expected_detail', 'expected_log_level'),
        [
            (ModelHTTPError(status_code=429, model_name='test'), 429, RATE_LIMITED_DETAIL, logging.WARNING),
            (ModelHTTPError(status_code=401, model_name='test'), 503, UNAVAILABLE_DETAIL, logging.ERROR),
            (ModelAPIError(model_name='test', message='Connection error.'), 503, UNAVAILABLE_DETAIL, logging.ERROR),
            (ReadTimeoutError(endpoint_url='https://bedrock.test'), 503, UNAVAILABLE_DETAIL, logging.ERROR),
            (
                UsageLimitExceeded('The next request would exceed the request_limit of 5'),
                503,
                'AI agent exceeded its usage limit.',
                logging.WARNING,
            ),
        ],
        ids=['http_429', 'http_401', 'api_error', 'botocore_read_timeout', 'usage_limit_exceeded'],
    )
    async def test_provider_error_mapping(
        self,
        client: AsyncClient,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
        caplog: pytest.LogCaptureFixture,
        exc: Exception,
        expected_status: int,
        expected_detail: str,
        expected_log_level: int,
    ) -> None:
        with test_examples_agent.override(model=build_raising_model(exc)):
            response = await client.post(
                '/v1/agents/examples/conversations',
                json={'model': 'gpt-5.4', 'question': 'How many examples do we have?'},
            )

        assert response.status_code == expected_status
        assert response.json()['detail'] == expected_detail
        assert [record.levelno for record in caplog.records if record.name == 'app.core.exception_handlers'] == [
            expected_log_level
        ]
{%- if cookiecutter.project_type == "fastapi_db_agent" %}

    @pytest.mark.parametrize('tool_name', ['count_examples', 'list_examples'])
    async def test_shared_session_tool_calls_do_not_overlap(
        self,
        client: AsyncClient,
        session: AsyncSession,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
        monkeypatch: pytest.MonkeyPatch,
        tool_name: str,
    ) -> None:
        service_method = getattr(ExampleService, tool_name)
        running = []

        async def exclusive_service_method(*args, **kwargs):
            assert not running, 'Tool calls overlap on the shared AsyncSession'
            running.append(tool_name)
            try:
                await asyncio.sleep(0)  # yield so a concurrently scheduled call would start here
                return await service_method(*args, **kwargs)
            finally:
                running.pop()

        monkeypatch.setattr(ExampleService, tool_name, exclusive_service_method)

        def call_tool_twice(messages: list, info: AgentInfo) -> ModelResponse:
            if len(messages) == 1:
                return ModelResponse(parts=[ToolCallPart(tool_name, {'payload': {}}) for _ in range(2)])
            return build_output_model_response(info, ExampleAgentResponse(answer='Done.'))

        with test_examples_agent.override(model=FunctionModel(call_tool_twice)):
            response = await client.post(
                '/v1/agents/examples/conversations', json={'model': 'gpt-5.4', 'question': 'How many examples?'}
            )

        assert response.status_code == 200
{%- endif %}
{%- endif %}
