{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response
from fastapi_pagination import Page, Params

from app.domains.examples.schemas import (
    Example,
    ExampleCreate,
    ExampleListFilters,
    ExampleListSorting,
    ExampleUpdate,
)
from app.domains.examples.service import ExampleService

router = APIRouter(tags=['Examples'])


@router.post('/examples', status_code=201)
async def add_example(creation: ExampleCreate, service: Annotated[ExampleService, Depends()]) -> Example:
    return await service.create_example(creation)


@router.get('/examples')
async def list_examples(
    filters: Annotated[ExampleListFilters, Query(default_factory=ExampleListFilters)],
    sorting: Annotated[ExampleListSorting, Depends()],
    pagination_params: Annotated[Params, Depends()],
    service: Annotated[ExampleService, Depends()],
) -> Page[Example]:
    return await service.list_examples(filters, sorting, pagination_params)


@router.get('/examples/{example_id}')
async def get_example(example_id: int, service: Annotated[ExampleService, Depends()]) -> Example:
    return await service.get_example_by_id(example_id)


@router.put('/examples/{example_id}')
async def change_example(
    example_id: int, updates: ExampleUpdate, service: Annotated[ExampleService, Depends()]
) -> Example:
    return await service.update_example(example_id, updates)


@router.delete('/examples/{example_id}', response_class=Response, status_code=204)
async def delete_example(example_id: int, service: Annotated[ExampleService, Depends()]) -> None:
    await service.delete_example_by_id(example_id)
{%- endif %}
