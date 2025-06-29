{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
from httpx import AsyncClient


async def test_health_route_success(client: AsyncClient) -> None:
    response = await client.get('/health-check')
    assert response.status_code == 204
    assert response.content == b'', 'API test failed'
{%- endif %}
