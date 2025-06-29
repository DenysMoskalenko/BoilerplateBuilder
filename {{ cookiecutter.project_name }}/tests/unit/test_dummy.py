{% if cookiecutter.project_type in ["cli_slim", "cli_db"] -%}
{%- if cookiecutter.project_type == "cli_db" %}
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.example import ExampleModel
{%- endif %}


async def test_placeholder() -> None:
    assert True

{%- if cookiecutter.project_type == "cli_db" %}


async def test_database_connection(session: AsyncSession) -> None:
    """Test that database connection works."""
    # Test we can query the database
    result = await session.execute(select(func.count(ExampleModel.id)))
    count = result.scalar()
    assert count is not None
    assert count >= 0
{%- endif %}
{%- endif %}
