{%- if cookiecutter.project_type == "fastapi_db" %}
from typing import Annotated

from fastapi import Depends
from pydantic import TypeAdapter
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.examples.schemas import Example, ExampleCreate, ExampleUpdate
from app.core.database import get_session
from app.core.exceptions import AlreadyExistError, NotFoundError
from app.models.example import ExampleModel


class ExampleService:
    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self._session = session

    async def get_example_by_id(self, example_id: int) -> Example:
        query = select(ExampleModel).filter(ExampleModel.id == example_id)

        example = await self._session.scalar(query)
        if example is None:
            raise NotFoundError(f'Example(id={example_id}) not found')
        return Example.model_validate(example)

    async def list_examples(self) -> list[Example]:
        query = select(ExampleModel)
        examples = (await self._session.scalars(query.order_by(ExampleModel.id))).fetchall()
        return TypeAdapter(list[Example]).validate_python(examples)

    async def create_example(self, creation: ExampleCreate) -> Example:
        async with self._session.begin_nested():
            await self._validate_example(creation)

            query = insert(ExampleModel).values(name=creation.name, birthday=creation.birthday).returning(ExampleModel)
            example = await self._session.scalar(query)

        return Example.model_validate(example)

    async def update_example(self, example_id: int, updates: ExampleUpdate) -> Example:
        async with self._session.begin_nested():
            await self.get_example_by_id(example_id)  # Validate example exists
            await self._validate_example(updates, current_example_id=example_id)

            query = (
                update(ExampleModel)
                .filter(ExampleModel.id == example_id)
                .values(name=updates.name, birthday=updates.birthday)
                .returning(ExampleModel)
            )
            updated_example = await self._session.scalar(query)

        return Example.model_validate(updated_example)

    async def delete_example_by_id(self, example_id: int) -> None:
        query = delete(ExampleModel).filter(ExampleModel.id == example_id)
        await self._session.execute(query)

    async def _validate_example(self, example_payload: ExampleCreate | ExampleUpdate, current_example_id: int | None = None) -> None:
        """Validate example data and check for duplicates."""
        query = select(ExampleModel).filter(ExampleModel.name == example_payload.name)
        if current_example_id is not None:
            query = query.filter(ExampleModel.id != current_example_id)

        example_exists = await self._session.scalar(select(query.exists()))
        if example_exists:
            raise AlreadyExistError('Example with this name already exists')
{%- endif %}
