{%- if cookiecutter.project_type != "fastapi_slim" -%}
from typing import NoReturn, cast

from fastapi import FastAPI, HTTPException, Request
from starlette import status
from starlette.types import ExceptionHandler
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from app.core.exceptions import AlreadyExistError, NotFoundError
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

from botocore.exceptions import ClientError
from openai import APIConnectionError, APITimeoutError, RateLimitError
{%- endif %}


def include_exception_handlers(app: FastAPI) -> None:
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    app.add_exception_handler(NotFoundError, cast(ExceptionHandler, not_found_exception_handler))
    app.add_exception_handler(AlreadyExistError, cast(ExceptionHandler, conflict_exception_handler))
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    app.add_exception_handler(ClientError, cast(ExceptionHandler, aws_client_error_exception_handler))
    app.add_exception_handler(RateLimitError, cast(ExceptionHandler, openai_rate_limit_exception_handler))
    app.add_exception_handler(APIConnectionError, cast(ExceptionHandler, openai_unavailable_exception_handler))
    app.add_exception_handler(APITimeoutError, cast(ExceptionHandler, openai_unavailable_exception_handler))
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


def not_found_exception_handler(request: Request, exc: NotFoundError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc) or 'Not Found') from exc


def conflict_exception_handler(request: Request, exc: AlreadyExistError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc) or 'Conflict') from exc
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}


def aws_client_error_exception_handler(request: Request, exc: ClientError) -> NoReturn:  # noqa: ARG001
    code = exc.response.get('Error', {}).get('Code')
    if code == 'ThrottlingException':
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='Too many requests to the AI provider. Please try again in a moment.',
        ) from exc
    if code in {'ServiceUnavailableException', 'TooManyRequestsException'}:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='AI provider temporarily unavailable. Please retry shortly.',
        ) from exc
    raise exc


def openai_rate_limit_exception_handler(request: Request, exc: RateLimitError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail='Too many requests to the AI provider. Please try again in a moment.',
    ) from exc


def openai_unavailable_exception_handler(request: Request, exc: APIConnectionError | APITimeoutError) -> NoReturn:  # noqa: ARG001
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail='AI provider temporarily unavailable. Please retry shortly.',
    ) from exc
{%- endif %}
{%- endif %}
