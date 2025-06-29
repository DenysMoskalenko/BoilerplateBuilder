{% if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] -%}
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

{%- if cookiecutter.project_type == "fastapi_db" %}
from app.api.examples.routes import router as examples_router
from app.api.health_checks.routes import router as health_checks_router
from app.core.config import get_settings
from app.core.exception_handlers import include_exception_handlers
from app.core.lifespan import lifespan
{%- else %}
from app.api.health_checks.routes import router as health_checks_router
from app.core.config import get_settings
from app.core.lifespan import lifespan
{%- endif %}

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
)


def create_app() -> FastAPI:
    settings = get_settings()

    _app = FastAPI(title=settings.PROJECT_NAME, version='0.1.0', lifespan=lifespan)
{%- if cookiecutter.project_type == "fastapi_db" %}
    include_exception_handlers(_app)

    _app.include_router(examples_router)
    _app.include_router(health_checks_router)
{%- else %}
    _app.include_router(health_checks_router)
{%- endif %}

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    return _app


app = create_app()
{% elif cookiecutter.project_type == "cli_db" -%}
import asyncio
import logging

from app.core.config import get_settings
from app.core.database import open_db_session
from app.models.example import ExampleModel

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
)


async def main() -> None:
    settings = get_settings()
    print(f'{settings.PROJECT_NAME} with database is ready...')  # noqa: T201
    
    # Example database usage
    async with open_db_session() as session:
        # You can add your database operations here
        # For example, count records in the example table
        from sqlalchemy import select, func
        
        result = await session.execute(select(func.count(ExampleModel.id)))
        count = result.scalar()
        print(f'Found {count} examples in database')  # noqa: T201


if __name__ == '__main__':
    asyncio.run(main())
{% else -%}
import asyncio
import logging

from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s %(message)s',
)


async def main() -> None:
    settings = get_settings()
    print(f'{settings.PROJECT_NAME} is ready...')  # noqa: T201


if __name__ == '__main__':
    asyncio.run(main())
{%- endif %}
