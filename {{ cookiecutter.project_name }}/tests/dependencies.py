from collections.abc import Callable, Generator, Sequence
from contextlib import contextmanager, ExitStack
from dataclasses import dataclass

from fastapi import FastAPI
from starlette.routing import Mount
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

from app.infrastructure.db.database import get_session
{%- endif %}


@dataclass(frozen=True, kw_only=True, slots=True)
class DepOverride:
    dependency: Callable
    override: Callable


def override_app_test_dependencies(app: FastAPI) -> None:
    deps: list[DepOverride] = [
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
        DepOverride(dependency=get_session, override=lambda: SessionFixtureDoesNotSetExplicitly),
{%- endif %}
    ]
    for dep in deps:
        override_dependency(app, dep.dependency, dep.override)


def override_dependency(app: FastAPI, dependency: Callable, override: Callable) -> None:
    app.dependency_overrides[dependency] = override

    for route in app.router.routes:
        if isinstance(route, Mount) and isinstance(route.app, FastAPI):
            route.app.dependency_overrides[dependency] = override


def _remove_override(app: FastAPI, dependency: Callable) -> None:
    app.dependency_overrides.pop(dependency, None)

    for route in app.router.routes:
        if isinstance(route, Mount) and isinstance(route.app, FastAPI):
            route.app.dependency_overrides.pop(dependency, None)


@contextmanager
def temporary_override(app: FastAPI, dependency: Callable, override: Callable) -> Generator[None, None, None]:
    """Temporarily override a FastAPI dependency and restore the previous state on exit."""
    previous = app.dependency_overrides.get(dependency)
    override_dependency(app, dependency, override)
    try:
        yield
    finally:
        if previous is not None:
            override_dependency(app, dependency, previous)
        else:
            _remove_override(app, dependency)


@contextmanager
def temporary_overrides(app: FastAPI, overrides: Sequence[DepOverride]) -> Generator[None, None, None]:
    """Temporarily override multiple FastAPI dependencies and restore the previous state on exit."""
    with ExitStack() as stack:
        for dep in overrides:
            stack.enter_context(temporary_override(app, dep.dependency, dep.override))
        yield
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}


class SessionFixtureDoesNotSetExplicitly: ...
{%- endif %}
