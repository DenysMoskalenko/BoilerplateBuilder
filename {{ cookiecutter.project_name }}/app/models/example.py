{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}
from datetime import date, datetime

from sqlalchemy import Date, DateTime, func, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExampleModel(Base):
    __tablename__ = 'examples'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    birthday: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
{%- endif %} 