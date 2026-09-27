{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from typing import Annotated
from unittest.mock import AsyncMock
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from types import SimpleNamespace
{%- endif %}

from fastapi import Depends, FastAPI
from httpx2 import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.examples.routes import router as examples_router
from app.domains.examples.service import ExampleService
from app.domains.health_checks.routes import router as health_router
from app.infrastructure.db import database
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
from app.infrastructure.llms.provider_bedrock import get_bedrock_client
from app.infrastructure.llms.provider_openai import get_openai_client
{%- endif %}


@pytest.mark.parametrize('fail_commit', [False, True])
@pytest.mark.parametrize('path', ['/examples/1', '/health/ready', '/cached', '/failing'])
async def test_session_finishes_before_response(monkeypatch, path: str, fail_commit: bool) -> None:
    events = []
    session = AsyncMock(spec=AsyncSession)

    async def commit() -> None:
        events.append('commit')
        if fail_commit:
            raise RuntimeError('commit failed')

    session.commit.side_effect = commit
    session.rollback.side_effect = lambda: events.append('rollback')
    session.close.side_effect = lambda: events.append('close')
    factory = lambda: session  # noqa: E731
    monkeypatch.setattr(database, 'async_session_factory', lambda: factory)
    app = FastAPI()
    app.include_router(examples_router)
    app.include_router(health_router)
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    app.dependency_overrides[get_bedrock_client] = lambda: SimpleNamespace(count_tokens=lambda **kwargs: {})
    app.dependency_overrides[get_openai_client] = lambda: SimpleNamespace(models=SimpleNamespace(list=AsyncMock()))
{%- endif %}

    @app.get('/cached')
    async def cached(
        first: Annotated[ExampleService, Depends(use_cache=False)],
        second: Annotated[ExampleService, Depends(use_cache=False)],
    ) -> dict:
        assert first is not second
        assert first._session is second._session is session
        return {}

    @app.get('/failing')
    async def failing(service: Annotated[ExampleService, Depends()]) -> None:
        raise RuntimeError('endpoint failed')

    async def record_response(scope, receive, send) -> None:
        async def record_send(message) -> None:
            if message['type'] == 'http.response.start':
                events.append('response')
            await send(message)

        await app(scope, receive, record_send)

    transport = ASGITransport(app=record_response, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.request('DELETE' if path == '/examples/1' else 'GET', path)

    expected_status = 204 if path == '/examples/1' else 200
    assert response.status_code == (500 if fail_commit or path == '/failing' else expected_status)
    assert events == ['rollback' if path == '/failing' else 'commit', 'close', 'response']
    session.close.assert_awaited_once()
{%- endif %}
