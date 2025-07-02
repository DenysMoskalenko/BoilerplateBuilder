{%- if cookiecutter.project_type == "fastapi_db" %}
from datetime import date, datetime, timedelta, UTC

from httpx import AsyncClient
from pydantic import TypeAdapter
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.examples.schemas import Example, ExampleCreate
from app.api.examples.service import ExampleService
from tests.factories import ExampleCreateFactory


async def create_test_example(session: AsyncSession) -> Example:
    example_creation = ExampleCreateFactory.build()
    example = await ExampleService(session).create_example(creation=ExampleCreate.model_validate(example_creation))
    return Example.model_validate(example)


class TestExamplesCreate:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        example_creation = ExampleCreateFactory.build()
        payload = {
            'name': example_creation.name,
            'birthday': example_creation.birthday and example_creation.birthday.isoformat(),
        }

        response = await client.post('/examples', json=payload)
        assert response.status_code == 201

        created_example = Example.model_validate(response.json())
        assert created_example.name == payload['name']
        assert (created_example.birthday and created_example.birthday.isoformat()) == payload['birthday']

    async def test_fail_already_exist(self, session: AsyncSession, client: AsyncClient):
        exist_example = await create_test_example(session)
        payload = {
            'name': exist_example.name,
            'birthday': date(year=1998, month=12, day=21).isoformat(),
        }

        response = await client.post('/examples', json=payload)
        assert response.status_code == 409
        assert response.json()['detail'] == 'Example with this name already exists'

    async def test_fail_unreal_birthday(self, client: AsyncClient):
        payload = {
            'name': ExampleCreateFactory.build().name,
            'birthday': (datetime.now(UTC) + timedelta(days=1)).date().isoformat(),
        }

        response = await client.post('/examples', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Value error, You cannot be born in the future'


class TestExamplesList:
    async def test_list_empty(self, session: AsyncSession, client: AsyncClient):
        response = await client.get('/examples')
        assert response.status_code == 200

        response_examples = response.json()
        assert response_examples == []

    async def test_list(self, session: AsyncSession, client: AsyncClient):
        example = await create_test_example(session)

        response = await client.get('/examples')
        assert response.status_code == 200

        response_examples = TypeAdapter(list[Example]).validate_python(response.json())
        assert response_examples == [example]


class TestExamplesGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient):
        example = await create_test_example(session)

        response = await client.get(f'/examples/{example.id}')
        assert response.status_code == 200

        response_example = Example.model_validate(response.json())
        assert response_example == example

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient):
        unreal_id = -9999999
        response = await client.get(f'/examples/{unreal_id}')
        assert response.status_code == 404
        assert response.json()['detail'] == f'Example(id={unreal_id}) not found'


@pytest.mark.skip
class TestExamplesUpdate: ...


@pytest.mark.skip
class TestExamplesDelete: ...
{%- endif %}
