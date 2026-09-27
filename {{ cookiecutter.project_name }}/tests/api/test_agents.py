{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
import logging
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
import asyncio
from contextlib import asynccontextmanager
{%- endif %}

from botocore.exceptions import ReadTimeoutError
from httpx2 import AsyncClient
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError, UsageLimitExceeded
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from pydantic_ai.messages import ModelResponse, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import FunctionModel
from sqlalchemy.ext.asyncio import AsyncSession
{%- endif %}
import pytest

from app.core.enums import AIModelName
from app.domains.examples_agent.schemas import ExampleAgentDeps, ExampleAgentResponse
from tests.mocks.agent_mocks import build_mock_model, build_raising_model
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from app.domains.examples.service import ExampleService
from tests.api.test_examples import create_test_example
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

    async def test_shared_session_tools_run_sequentially(
        self, client: AsyncClient, session: AsyncSession, test_examples_agent, monkeypatch
    ) -> None:
        example = await create_test_example(session, name='Shared session example')
        active = False
        calls = []

        @asynccontextmanager
        async def tool_call(name):
            nonlocal active
            assert not active, 'Tools must not use the shared session concurrently'
            active = True
            calls.append(name)
            try:
                await asyncio.sleep(0)  # Let another scheduled tool try to enter.
                yield
            finally:
                active = False

        original_count = ExampleService.count_examples
        original_list = ExampleService.list_examples

        async def count(service, *args, **kwargs):
            async with tool_call('count_examples'):
                return await original_count(service, *args, **kwargs)

        async def list_examples(service, *args, **kwargs):
            async with tool_call('list_examples'):
                return await original_list(service, *args, **kwargs)

        monkeypatch.setattr(ExampleService, 'count_examples', count)
        monkeypatch.setattr(ExampleService, 'list_examples', list_examples)

        def model(messages, info):
            if not calls:
                return ModelResponse(parts=[
                    ToolCallPart('count_examples', {'payload': {}}, tool_call_id='count'),
                    ToolCallPart('list_examples', {'payload': {}}, tool_call_id='list'),
                ])
            results = {part.tool_name: part.content for part in messages[-1].parts if isinstance(part, ToolReturnPart)}
            assert results['count_examples'] == 1
            assert results['list_examples'][0].id == example.id
            return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, {'answer': 'Found one example.'})])

        with test_examples_agent.override(model=FunctionModel(model)):
            response = await client.post(
                '/v1/agents/examples/conversations', json={'model': 'gpt-5.4', 'question': 'Count and list examples.'}
            )

        assert response.status_code == 200
        assert response.json() == {'answer': 'Found one example.'}
        assert sorted(calls) == ['count_examples', 'list_examples']
{%- endif %}
{%- endif %}
