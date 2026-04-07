{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from logging import getLogger
from typing import Annotated

from fastapi import Depends
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate
from pydantic import TypeAdapter
from sqlalchemy import delete, func, insert, Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.examples.schemas import (
    Example,
    ExampleCreate,
    ExampleListFilters,
    ExampleListSorting,
    ExampleUpdate,
)
from app.core.exceptions import AlreadyExistError, NotFoundError
from app.infrastructure.db.database import get_session
from app.infrastructure.db.filters import apply_contains_filter
from app.infrastructure.db.models.example import ExampleModel
{%- if cookiecutter.use_otel_observability == "yes" %}
from app.observability.metrics import counters
{%- endif %}

_logger = getLogger(__name__)


class ExampleService:
    EXAMPLE_LIST_ADAPTER: TypeAdapter[list[Example]] = TypeAdapter(list[Example])

    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self._session = session

    async def get_example_by_id(self, example_id: int) -> Example:
        query = select(ExampleModel).filter(ExampleModel.id == example_id)

        example = await self._session.scalar(query)
        if example is None:
            raise NotFoundError(f'Example(id={example_id}) not found')
        return Example.model_validate(example)

    async def list_examples(
        self,
        filters: ExampleListFilters,
        sorting: ExampleListSorting,
        pagination_params: Params,
    ) -> Page[Example]:
{%- if cookiecutter.use_otel_observability == "yes" %}
        has_filters = any([filters.ids, filters.name, filters.description, filters.created_from, filters.created_to])
        counters.search_queries_total.labels(resource='examples', has_filters=str(has_filters).lower()).inc()
{%- endif %}
        query = select(ExampleModel)
        query = self._apply_filters(query, filters)
        query = sorting.sort_query(query, ExampleModel)
        return await apaginate(
            self._session,
            query,
            params=pagination_params,
            transformer=lambda examples: self.EXAMPLE_LIST_ADAPTER.validate_python(examples),
        )

{%- if cookiecutter.project_type == "fastapi_db_agent" %}

    async def count_examples(self, filters: ExampleListFilters) -> int:
        query = select(func.count()).select_from(ExampleModel)
        query = self._apply_filters(query, filters)
        count = await self._session.scalar(query)
        if count is None:
            return 0
        return int(count)
{%- endif %}

    async def create_example(self, creation: ExampleCreate) -> Example:
        async with self._session.begin_nested():
            await self._validate_example_unique(creation)

            query = (
                insert(ExampleModel)
                .values(
                    name=creation.name,
                    description=creation.description,
                    birthday=creation.birthday,
                )
                .returning(ExampleModel)
            )
            example = await self._session.scalar(query)

        return Example.model_validate(example)

    async def update_example(self, example_id: int, updates: ExampleUpdate) -> Example:
        async with self._session.begin_nested():
            await self._validate_example_unique(updates, exclude_example_id=example_id)

            query = (
                update(ExampleModel)
                .filter(ExampleModel.id == example_id)
                .values(
                    name=updates.name,
                    description=updates.description,
                    birthday=updates.birthday,
                )
                .returning(ExampleModel)
            )
            example = await self._session.scalar(query)

        if example is None:
            raise NotFoundError(f'Example(id={example_id}) not found')
        return Example.model_validate(example)

    async def delete_example_by_id(self, example_id: int) -> None:
        async with self._session.begin_nested():
            query = delete(ExampleModel).filter(ExampleModel.id == example_id).returning(ExampleModel.id)
            deleted_example_id = await self._session.scalar(query)
            if deleted_example_id is None:
                _logger.info('Example with id=%s not found but was requested for deletion', example_id)

    def _apply_filters(self, query: Select, filters: ExampleListFilters) -> Select:
        if filters.ids is not None:
            query = query.where(ExampleModel.id.in_(filters.ids))
        if filters.name is not None:
            query = apply_contains_filter(query, ExampleModel.name, filters.name)
        if filters.description is not None:
            query = apply_contains_filter(query, ExampleModel.description, filters.description)
        if filters.created_from is not None:
            query = query.where(ExampleModel.created_at >= filters.created_from)
        if filters.created_to is not None:
            query = query.where(ExampleModel.created_at <= filters.created_to)
        return query

    async def _validate_example_unique(
        self, example_payload: ExampleCreate | ExampleUpdate, *, exclude_example_id: int | None = None
    ) -> None:
        query = select(ExampleModel.id).where(ExampleModel.name == example_payload.name)
        if exclude_example_id is not None:
            query = query.where(ExampleModel.id != exclude_example_id)

        example_exists = await self._session.scalar(select(query.exists()))
        if example_exists:
            raise AlreadyExistError('Example with this name already exists')
{%- endif %}
