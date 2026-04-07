{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from typing import Any, cast

from botocore.exceptions import ClientError
from httpx import AsyncClient, Request, Response
from openai import APIConnectionError, RateLimitError
from pydantic_ai import Agent
import pytest

from app.agents.examples_agent.schemas import ExampleAgentDeps
from app.api.v1.agents.schemas import ExampleAgentResponse
from app.core.enums import AIModelName
from tests.mocks.agent_mocks import build_mock_model, build_raising_model


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

    async def test_bedrock_throttling_maps_to_429(
        self,
        client: AsyncClient,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
    ) -> None:
        exc = ClientError(
            error_response=cast(
                Any,
                {
                    'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'},
                    'ResponseMetadata': {'HTTPStatusCode': 400},
                },
            ),
            operation_name='Converse',
        )
        with test_examples_agent.override(model=build_raising_model(exc)):
            response = await client.post(
                '/v1/agents/examples/conversations',
                json={'model': 'sonnet-4.6', 'question': 'How many examples do we have?'},
            )

        assert response.status_code == 429
        assert response.json()['detail'] == 'Too many requests to the AI provider. Please try again in a moment.'

    async def test_openai_rate_limit_maps_to_429(
        self,
        client: AsyncClient,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
    ) -> None:
        request = Request('POST', 'https://api.openai.com/v1/responses')
        response = Response(429, request=request)
        exc = RateLimitError('rate limited', response=response, body={'error': {'message': 'rate limited'}})
        with test_examples_agent.override(model=build_raising_model(exc)):
            response = await client.post(
                '/v1/agents/examples/conversations',
                json={'model': 'gpt-5.4', 'question': 'How many examples do we have?'},
            )

        assert response.status_code == 429
        assert response.json()['detail'] == 'Too many requests to the AI provider. Please try again in a moment.'

    async def test_openai_connection_error_maps_to_503(
        self,
        client: AsyncClient,
        test_examples_agent: Agent[ExampleAgentDeps, ExampleAgentResponse],
    ) -> None:
        exc = APIConnectionError(
            message='Connection error.',
            request=Request('POST', 'https://api.openai.com/v1/responses'),
        )
        with test_examples_agent.override(model=build_raising_model(exc)):
            response = await client.post(
                '/v1/agents/examples/conversations',
                json={'model': 'gpt-5.4', 'question': 'How many examples do we have?'},
            )

        assert response.status_code == 503
        assert response.json()['detail'] == 'AI provider temporarily unavailable. Please retry shortly.'
{%- endif %}
