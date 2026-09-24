{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from botocore.exceptions import ReadTimeoutError
from httpx2 import AsyncClient
from pydantic_ai import Agent
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError, UsageLimitExceeded
import pytest

from app.core.enums import AIModelName
from app.domains.examples_agent.schemas import ExampleAgentDeps, ExampleAgentResponse
from tests.mocks.agent_mocks import build_mock_model, build_raising_model

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
        ('exc', 'expected_status', 'expected_detail'),
        [
            (ModelHTTPError(status_code=429, model_name='test'), 429, RATE_LIMITED_DETAIL),
            (ModelHTTPError(status_code=500, model_name='test'), 503, UNAVAILABLE_DETAIL),
            (ModelAPIError(model_name='test', message='Connection error.'), 503, UNAVAILABLE_DETAIL),
            (ReadTimeoutError(endpoint_url='https://bedrock.test'), 503, UNAVAILABLE_DETAIL),
            (
                UsageLimitExceeded('The next request would exceed the request_limit of 5'),
                503,
                'AI agent exceeded its usage limit. Please retry shortly.',
            ),
        ],
        ids=['http_429', 'http_500', 'api_error', 'botocore_read_timeout', 'usage_limit_exceeded'],
    )
    async def test_provider_error_mapping(
        self,
        client: AsyncClient,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
        exc: Exception,
        expected_status: int,
        expected_detail: str,
    ) -> None:
        with test_examples_agent.override(model=build_raising_model(exc)):
            response = await client.post(
                '/v1/agents/examples/conversations',
                json={'model': 'gpt-5.4', 'question': 'How many examples do we have?'},
            )

        assert response.status_code == expected_status
        assert response.json()['detail'] == expected_detail
{%- endif %}
