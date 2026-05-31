{%- if cookiecutter.use_otel_observability == "yes" %}
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from functools import wraps
import inspect
from typing import cast, overload, ParamSpec, TypeVar

from opentelemetry import trace as otel_trace
from opentelemetry.trace.status import Status, StatusCode

tracer = otel_trace.get_tracer(__name__)

P = ParamSpec('P')
R = TypeVar('R')


@overload
def trace(_func: Callable[P, R]) -> Callable[P, R]: ...


@overload
def trace(*, span_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]: ...


def trace(
    _func: Callable[P, R] | None = None, *, span_name: str | None = None
) -> Callable[[Callable[P, R]], Callable[P, R]] | Callable[P, R]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        func_name = getattr(func, '__name__', func.__class__.__name__)
        func_qualname = getattr(func, '__qualname__', func.__class__.__name__)
        final_span_name = span_name if span_name is not None else f'{func.__module__}.{func_qualname}'

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with _trace_span(final_span_name, func_name):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            async_func = cast(Callable[P, Awaitable[R]], func)
            with _trace_span(final_span_name, func_name):
                return await async_func(*args, **kwargs)

        if inspect.iscoroutinefunction(func):
            return cast(Callable[P, R], async_wrapper)
        return sync_wrapper

    if _func is None:
        return decorator
    return decorator(_func)


@contextmanager
def _trace_span(span_name: str, func_name: str) -> Generator[None, None, None]:
    """Create a span around a decorated call and mark it by outcome."""
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute('code.function', func_name)
        try:
            yield
        except Exception as exc:
            span.set_status(Status(StatusCode.ERROR, description=str(exc)))
            raise
        else:
            span.set_status(Status(StatusCode.OK))
{%- endif %}
