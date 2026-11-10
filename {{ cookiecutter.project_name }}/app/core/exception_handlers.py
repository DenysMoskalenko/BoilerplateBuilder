{%- if cookiecutter.project_type != "fastapi_slim" -%}
{% if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] -%}
import logging
{% endif -%}
from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status
from starlette.types import ExceptionHandler
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AlreadyExistError, NotFoundError
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from botocore.exceptions import BotoCoreError
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError, UnexpectedModelBehavior, UsageLimitExceeded

_logger = logging.getLogger(__name__)
{%- endif %}


def include_exception_handlers(app: FastAPI) -> None:
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    app.add_exception_handler(NotFoundError, cast(ExceptionHandler, not_found_exception_handler))
    app.add_exception_handler(AlreadyExistError, cast(ExceptionHandler, conflict_exception_handler))
    app.add_exception_handler(IntegrityError, cast(ExceptionHandler, integrity_error_exception_handler))
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    app.add_exception_handler(ModelHTTPError, cast(ExceptionHandler, model_http_error_exception_handler))
    app.add_exception_handler(ModelAPIError, cast(ExceptionHandler, ai_provider_unavailable_exception_handler))
    # Bedrock wraps ClientError, timeouts and connection errors; any other BotoCoreError reaches the app unwrapped
    app.add_exception_handler(BotoCoreError, cast(ExceptionHandler, ai_provider_unavailable_exception_handler))
    app.add_exception_handler(UsageLimitExceeded, cast(ExceptionHandler, usage_limit_exceeded_exception_handler))
    app.add_exception_handler(
        UnexpectedModelBehavior, cast(ExceptionHandler, unexpected_model_behavior_exception_handler)
    )
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={'detail': str(exc) or 'Not Found'})


async def conflict_exception_handler(request: Request, exc: AlreadyExistError) -> JSONResponse:  # noqa: ARG001
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={'detail': str(exc) or 'Conflict'})


async def integrity_error_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:  # noqa: ARG001
    # A uniqueness SELECT cannot see a concurrent transaction's uncommitted row; only the constraint decides
    if isinstance(exc.orig, UniqueViolation):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={'detail': 'Conflict'})
    raise exc
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}


async def model_http_error_exception_handler(request: Request, exc: ModelHTTPError) -> JSONResponse:
    if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        _logger.warning('AI provider rate limited the request: %s', exc)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={'detail': 'Too many requests to the AI provider. Please try again in a moment.'},
        )
    return await ai_provider_unavailable_exception_handler(request, exc)


async def ai_provider_unavailable_exception_handler(
    request: Request,  # noqa: ARG001
    exc: ModelAPIError | BotoCoreError,
) -> JSONResponse:
    _logger.error('AI provider request failed', exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={'detail': 'AI provider temporarily unavailable. Please retry shortly.'},
    )


async def usage_limit_exceeded_exception_handler(request: Request, exc: UsageLimitExceeded) -> JSONResponse:  # noqa: ARG001
    _logger.warning('AI agent exceeded its usage limit: %s', exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={'detail': 'AI agent exceeded its usage limit.'},
    )


async def unexpected_model_behavior_exception_handler(
    request: Request,  # noqa: ARG001
    exc: UnexpectedModelBehavior,
) -> JSONResponse:
    _logger.error('AI model returned an unexpected response', exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={'detail': 'AI model returned an unexpected response.'},
    )
{%- endif %}
{%- endif %}
