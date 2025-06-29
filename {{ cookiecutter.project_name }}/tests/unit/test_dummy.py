{% if cookiecutter.project_type in ["cli_slim", "cli_db"] -%}
async def test_placeholder() -> None:
    assert True

{%- if cookiecutter.project_type == "cli_db" %}
from sqlalchemy.ext.asyncio import AsyncSession

async def test_database_connection(session: AsyncSession) -> None:
    """Test that database connection works."""
    from app.models.example import ExampleModel
    from sqlalchemy import select, func
    
    # Test we can query the database
    result = await session.execute(select(func.count(ExampleModel.id)))
    count = result.scalar()
    assert count is not None
    assert count >= 0
{%- endif %}
{%- endif %}
