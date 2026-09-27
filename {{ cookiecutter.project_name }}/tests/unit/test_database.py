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


@pytest.fixture
def db_session(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    monkeypatch.setattr(database, 'async_session_factory', lambda: lambda: session)
    return session


@pytest.mark.parametrize('fail_commit', [False, True], ids=['success', 'commit_failure'])
@pytest.mark.parametrize(('method', 'path', 'status'), [('DELETE', '/examples/1', 204), ('GET', '/health/ready', 200)])
async def test_session_finishes_before_response(
    db_session: AsyncMock, method: str, path: str, status: int, fail_commit: bool
) -> None:
    if fail_commit:
        db_session.commit.side_effect = RuntimeError('commit failed')
    app = FastAPI()
    app.include_router(examples_router)
    app.include_router(health_router)
{%- if cookiecutter.project_type == "fastapi_db_agent" %}
    app.dependency_overrides[get_bedrock_client] = lambda: SimpleNamespace(count_tokens=lambda **kwargs: {})
    app.dependency_overrides[get_openai_client] = lambda: SimpleNamespace(models=SimpleNamespace(list=AsyncMock()))
{%- endif %}
    sent_statuses = []

    async def record_response(scope, receive, send) -> None:
        async def record_send(message) -> None:
            if message['type'] == 'http.response.start':
                db_session.commit.assert_awaited_once()
                db_session.close.assert_awaited_once()
                sent_statuses.append(message['status'])
            await send(message)

        await app(scope, receive, record_send)

    async with AsyncClient(transport=ASGITransport(app=record_response), base_url='http://test') as client:
        if fail_commit:
            with pytest.raises(RuntimeError, match=r'^commit failed$'):
                await client.request(method, path)
            assert sent_statuses == [500]
        else:
            response = await client.request(method, path)
            assert response.status_code == status
            assert sent_statuses == [status]
            db_session.rollback.assert_not_awaited()


async def test_session_rolls_back_and_preserves_endpoint_error(db_session: AsyncMock) -> None:
    app = FastAPI()
    error = RuntimeError('endpoint failed')

    @app.get('/failing')
    async def failing(service: Annotated[ExampleService, Depends()]) -> None:
        raise error

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        with pytest.raises(RuntimeError, match=r'^endpoint failed$') as raised:
            await client.get('/failing')

    assert raised.value is error
    db_session.rollback.assert_awaited_once()
    db_session.close.assert_awaited_once()
    db_session.commit.assert_not_awaited()


async def test_session_is_cached_across_service_instances(db_session: AsyncMock) -> None:
    app = FastAPI()

    @app.get('/cached')
    async def cached(
        first: Annotated[ExampleService, Depends(use_cache=False)],
        second: Annotated[ExampleService, Depends(use_cache=False)],
    ) -> None:
        assert first is not second

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.get('/cached')

    assert response.status_code == 200
    db_session.commit.assert_awaited_once()
    db_session.close.assert_awaited_once()
{%- endif %}
