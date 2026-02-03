{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
from dataclasses import dataclass
from typing import Any, Callable, cast

from fastapi import FastAPI
from starlette.routing import Mount


@dataclass(frozen=True, kw_only=True, slots=True)
class _DepOverride:
    dependency: Callable
    override: Callable


def override_app_test_dependencies(app: FastAPI):
    deps: list[_DepOverride] = [
        # _DepOverride(dependency=get_session, override=lambda: get_test_session),  # Override your deps for session
    ]
    for dep in deps:
        override_dependency(app, dep.dependency, dep.override)


def override_dependency(app: FastAPI, dependency: Callable, override: Callable) -> None:
    app.dependency_overrides[dependency] = override

    for route in app.router.routes:
        if isinstance(route, Mount):
            if hasattr(route.app, 'dependency_overrides'):
                app_with_overrides = cast(Any, route.app)
                app_with_overrides.dependency_overrides[dependency] = override
{%- endif %}
