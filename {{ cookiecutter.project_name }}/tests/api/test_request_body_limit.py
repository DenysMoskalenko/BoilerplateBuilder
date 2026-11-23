from fastapi import FastAPI
from httpx2 import AsyncClient


async def test_request_body_over_limit_is_rejected_on_any_path(app: FastAPI, client: AsyncClient) -> None:
    assert app.max_body_size is not None

    response = await client.post('/', content=b'x' * (app.max_body_size + 1))

    assert response.status_code == 413
