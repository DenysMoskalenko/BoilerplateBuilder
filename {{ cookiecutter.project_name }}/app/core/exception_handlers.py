{%- if cookiecutter.project_type == "fastapi_db" %}
from typing import cast

from fastapi import FastAPI, HTTPException, Request
from starlette import status
from starlette.types import ExceptionHandler

from app.core.exceptions import AlreadyExistError, NotFoundError


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, cast(ExceptionHandler, not_found_exception_handler))
    app.add_exception_handler(AlreadyExistError, cast(ExceptionHandler, conflict_exception_handler))


def not_found_exception_handler(request: Request, exc: NotFoundError) -> None:  # noqa: ARG001
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc) or 'Not Found') from exc


def conflict_exception_handler(request: Request, exc: AlreadyExistError) -> None:  # noqa: ARG001
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc) or 'Conflict') from exc
{%- endif %}
