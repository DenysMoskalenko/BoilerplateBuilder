{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from collections.abc import Callable, Iterator
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from tests.dependencies import temporary_override


def generate_test_agent(
    app: FastAPI,
    dependency: Callable,
    agent_builder: Callable[[Any], Agent[Any, Any]],
) -> Iterator[Agent[Any, Any]]:
    agent = agent_builder(TestModel())
    with temporary_override(app, dependency, lambda: agent):
        yield agent


def build_mock_model(response: BaseModel) -> FunctionModel:
    def _cb(messages: list, info: AgentInfo) -> ModelResponse:
        return _build_output_model_response(info, response)

    return FunctionModel(_cb)


def build_raising_model(exc: Exception) -> FunctionModel:
    def _cb(messages: list, info: AgentInfo) -> ModelResponse:
        raise exc

    return FunctionModel(_cb)


def _build_output_model_response(info: AgentInfo, response: BaseModel) -> ModelResponse:
    payload = response.model_dump(mode='json')
    payload_keys = set(payload.keys())
    for output_tool in info.output_tools:
        properties = (output_tool.parameters_json_schema or {}).get('properties', {})
        if set(properties.keys()).issubset(payload_keys):
            return ModelResponse(parts=[ToolCallPart(tool_name=output_tool.name, args=payload)])
    raise AssertionError('Could not resolve final result tool')
{%- endif %}
