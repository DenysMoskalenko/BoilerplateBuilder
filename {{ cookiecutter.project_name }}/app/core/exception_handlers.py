{%- if cookiecutter.project_type != "fastapi_slim" -%}
from typing import NoReturn, cast

from fastapi import FastAPI, HTTPException, Request
from starlette import status
from starlette.types import ExceptionHandler
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from app.core.exceptions import AlreadyExistError, NotFoundError
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from botocore.exceptions import BotoCoreError
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError, UsageLimitExceeded
{%- endif %}


def include_exception_handlers(app: FastAPI) -> None:
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    app.add_exception_handler(NotFoundError, cast(ExceptionHandler, not_found_exception_handler))
    app.add_exception_handler(AlreadyExistError, cast(ExceptionHandler, conflict_exception_handler))
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    app.add_exception_handler(ModelHTTPError, cast(ExceptionHandler, model_http_error_exception_handler))
    app.add_exception_handler(ModelAPIError, cast(ExceptionHandler, ai_provider_unavailable_exception_handler))
    # Bedrock wraps only ClientError; BotoCoreError (timeouts, connection errors) reaches the app unwrapped
    app.add_exception_handler(BotoCoreError, cast(ExceptionHandler, ai_provider_unavailable_exception_handler))
    app.add_exception_handler(UsageLimitExceeded, cast(ExceptionHandler, usage_limit_exceeded_exception_handler))
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


def not_found_exception_handler(request: Request, exc: NotFoundError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc) or 'Not Found') from exc


def conflict_exception_handler(request: Request, exc: AlreadyExistError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc) or 'Conflict') from exc
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}


def model_http_error_exception_handler(request: Request, exc: ModelHTTPError) -> NoReturn:
    if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='Too many requests to the AI provider. Please try again in a moment.',
        ) from exc
    ai_provider_unavailable_exception_handler(request, exc)


def ai_provider_unavailable_exception_handler(request: Request, exc: ModelAPIError | BotoCoreError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail='AI provider temporarily unavailable. Please retry shortly.',
    ) from exc


def usage_limit_exceeded_exception_handler(request: Request, exc: UsageLimitExceeded) -> NoReturn:  # noqa: ARG001
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail='AI agent exceeded its usage limit. Please retry shortly.',
    ) from exc
{%- endif %}
{%- endif %}
