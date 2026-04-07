{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from typing import Literal, TypeAlias

from pydantic import BaseModel, Field
from sqlalchemy import asc, desc, Select

from app.infrastructure.db.database import Base

SortingOrder: TypeAlias = Literal['asc', 'desc']


class BaseListSorting(BaseModel):
    sort_by: str = Field(description='Sorting field')
    sort_order: SortingOrder = Field(default='desc', description='Sorting direction')

    def sort_query(self, query: Select, model: type[Base]) -> Select:
        direction = asc if self.sort_order == 'asc' else desc
        if not hasattr(model, self.sort_by):
            raise ValueError(f'Invalid sort field: {self.sort_by}')
        order_column = getattr(model, self.sort_by)
        return query.order_by(direction(order_column))
{%- endif %}
