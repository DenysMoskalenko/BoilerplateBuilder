{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from datetime import date, datetime, timedelta, UTC

from fastapi_pagination import Page
from httpx import AsyncClient
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.examples.schemas import Example, ExampleCreate
from app.services.example_service import ExampleService
from tests.factories import ExampleCreateFactory


async def create_test_example(
    session: AsyncSession,
    *,
    name: str | None = None,
    description: str | None = None,
    birthday: date | None = None,
) -> Example:
    payload = ExampleCreateFactory.build(
        factory_use_construct=False,
        **({'name': name} if name is not None else {}),
        **({'description': description} if description is not None else {}),
        **({'birthday': birthday} if birthday is not None else {}),
    )
    example = await ExampleService(session).create_example(payload)
    await session.flush()
    return example


class TestExamplesCreate:
    async def test_success(self, session: AsyncSession, client: AsyncClient) -> None:
        payload = ExampleCreateFactory.build()

        response = await client.post('/v1/examples', json=payload.model_dump(mode='json'))
        assert response.status_code == 201

        actual = response.json()
        assert Example.model_validate(actual)
        expected = payload.model_dump(mode='json') | {
            'id': actual['id'],
            'created_at': actual['created_at'],
            'updated_at': actual['updated_at'],
        }
        assert actual == expected

    async def test_fail_duplicate_identity(self, session: AsyncSession, client: AsyncClient) -> None:
        existing_example = await create_test_example(session)
        payload = ExampleCreateFactory.build(name=existing_example.name)

        response = await client.post('/v1/examples', json=payload.model_dump(mode='json'))
        assert response.status_code == 409
        assert response.json()['detail'] == 'Example with this name already exists'

    async def test_fail_unreal_birthday(self, session: AsyncSession, client: AsyncClient) -> None:
        payload = ExampleCreateFactory.build().model_dump(mode='json')
        payload['birthday'] = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()

        response = await client.post('/v1/examples', json=payload)
        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Value error, Birthday cannot be in the future'


class TestExamplesList:
    EXAMPLE_PAGE_ADAPTER: TypeAdapter[Page[Example]] = TypeAdapter(Page[Example])

    async def test_list_empty(self, session: AsyncSession, client: AsyncClient) -> None:
        response = await client.get('/v1/examples')
        assert response.status_code == 200

        examples = self.EXAMPLE_PAGE_ADAPTER.validate_python(response.json())
        assert examples.items == []
        assert examples.total == 0

    async def test_list_paginates(self, session: AsyncSession, client: AsyncClient) -> None:
        first_example = await create_test_example(session, name='Example A')
        second_example = await create_test_example(session, name='Example B')
        assert first_example.name < second_example.name

        response = await client.get(
            '/v1/examples',
            params={'page': 2, 'size': 1, 'sort_by': 'name', 'sort_order': 'asc'},
        )
        assert response.status_code == 200

        actual = response.json()
        expected = {
            'items': [second_example.model_dump(mode='json')],
            'total': 2,
            'page': 2,
            'size': 1,
            'pages': 2,
        }
        assert actual == expected

    async def test_list_filters(self, session: AsyncSession, client: AsyncClient) -> None:
        await create_test_example(session, name='Alpha', description='First item')
        matching_example = await create_test_example(session, name='Alpha Beta', description='Second item')
        await create_test_example(session, name='Gamma', description='Third item')

        response = await client.get('/v1/examples', params={'name': 'alpha', 'description': 'Second'})
        assert response.status_code == 200

        examples = response.json()['items']
        assert examples == [matching_example.model_dump(mode='json')]


class TestExamplesGet:
    async def test_success(self, session: AsyncSession, client: AsyncClient) -> None:
        example = await create_test_example(session)

        response = await client.get(f'/v1/examples/{example.id}')

        assert response.status_code == 200
        assert example == Example.model_validate(response.json())

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient) -> None:
        unreal_id = -9999999

        response = await client.get(f'/v1/examples/{unreal_id}')

        assert response.status_code == 404
        assert response.json()['detail'] == f'Example(id={unreal_id}) not found'


class TestExamplesUpdate:
    async def test_success(self, session: AsyncSession, client: AsyncClient) -> None:
        exist_example = await create_test_example(session)
        payload = ExampleCreate.model_validate(exist_example.model_dump(mode='json'))
        payload.name = f'{payload.name} Updated'

        response = await client.put(f'/v1/examples/{exist_example.id}', json=payload.model_dump(mode='json'))
        assert response.status_code == 200

        updated_example = Example.model_validate(response.json())
        assert updated_example.model_dump(exclude={'name'}) == exist_example.model_dump(exclude={'name'})
        assert updated_example.name == payload.name

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient) -> None:
        unreal_id = -9999999

        response = await client.put(
            f'/v1/examples/{unreal_id}',
            json=ExampleCreateFactory.build().model_dump(mode='json'),
        )

        assert response.status_code == 404
        assert response.json()['detail'] == f'Example(id={unreal_id}) not found'

    async def test_fail_duplicate_identity(self, session: AsyncSession, client: AsyncClient) -> None:
        first_example = await create_test_example(session)
        second_example = await create_test_example(session)
        payload = ExampleCreateFactory.build(name=first_example.name)

        response = await client.put(f'/v1/examples/{second_example.id}', json=payload.model_dump(mode='json'))

        assert response.status_code == 409
        assert response.json()['detail'] == 'Example with this name already exists'

    async def test_fail_unreal_birthday(self, session: AsyncSession, client: AsyncClient) -> None:
        example = await create_test_example(session)
        payload = ExampleCreateFactory.build().model_dump(mode='json')
        payload['birthday'] = (datetime.now(UTC) + timedelta(days=1)).date().isoformat()

        response = await client.put(f'/v1/examples/{example.id}', json=payload)

        assert response.status_code == 422
        assert response.json()['detail'][0]['msg'] == 'Value error, Birthday cannot be in the future'


class TestExamplesDelete:
    async def test_success(self, session: AsyncSession, client: AsyncClient) -> None:
        example = await create_test_example(session)

        response = await client.delete(f'/v1/examples/{example.id}')
        assert response.status_code == 204

        get_response = await client.get(f'/v1/examples/{example.id}')
        assert get_response.status_code == 404

    async def test_fail_not_found(self, session: AsyncSession, client: AsyncClient) -> None:
        unreal_id = -9999999

        response = await client.delete(f'/v1/examples/{unreal_id}')

        assert response.status_code == 204
{%- endif %}
