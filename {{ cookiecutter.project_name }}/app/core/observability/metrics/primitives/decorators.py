{%- if cookiecutter.use_otel_observability == "yes" %}
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from functools import wraps
import inspect
import time
from typing import cast, overload, ParamSpec, TypeAlias, TypeVar

from prometheus_client import Histogram
from prometheus_client.metrics import Counter as PromCounter, Gauge as PromGauge

Hook: TypeAlias = Callable[[], None] | None
InflightMetric: TypeAlias = PromGauge
CompletionMetric: TypeAlias = PromCounter
P = ParamSpec('P')
T = TypeVar('T')


def track_inflight(gauge_or_child: InflightMetric) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        return _wrap_with_hooks(
            func,
            before=gauge_or_child.inc,
            after=gauge_or_child.dec,
            on_exception=gauge_or_child.dec,
        )

    return decorator


def increment_after(
    counter_or_child: CompletionMetric, success_only: bool = True
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        on_exception = None if success_only else counter_or_child.inc
        return _wrap_with_hooks(func, before=None, after=counter_or_child.inc, on_exception=on_exception)

    return decorator


def increment_on_error(counter_or_child: CompletionMetric) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        return _wrap_with_hooks(func, before=None, after=None, on_exception=counter_or_child.inc)

    return decorator


def track_latency(histogram: Histogram) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if inspect.iscoroutinefunction(func):
            async_func = cast(Callable[P, Awaitable[T]], func)

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                with _observe_latency(histogram):
                    return await async_func(*args, **kwargs)

            return cast(Callable[P, T], async_wrapper)

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with _observe_latency(histogram):
                return func(*args, **kwargs)

        return sync_wrapper

    return decorator


@overload
def _wrap_with_hooks(
    func: Callable[P, Awaitable[T]],
    *,
    before: Hook,
    after: Hook,
    on_exception: Hook = None,
) -> Callable[P, Awaitable[T]]: ...


@overload
def _wrap_with_hooks(
    func: Callable[P, T],
    *,
    before: Hook,
    after: Hook,
    on_exception: Hook = None,
) -> Callable[P, T]: ...


def _wrap_with_hooks(
    func: Callable[P, T] | Callable[P, Awaitable[T]],
    *,
    before: Hook,
    after: Hook,
    on_exception: Hook = None,
) -> Callable[P, T] | Callable[P, Awaitable[T]]:
    if inspect.iscoroutinefunction(func):
        async_func = cast(Callable[P, Awaitable[T]], func)

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            with _hook_scope(before=before, after=after, on_exception=on_exception):
                return await async_func(*args, **kwargs)

        return async_wrapper

    sync_func = cast(Callable[P, T], func)

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        with _hook_scope(before=before, after=after, on_exception=on_exception):
            return sync_func(*args, **kwargs)

    return sync_wrapper


@contextmanager
def _hook_scope(*, before: Hook, after: Hook, on_exception: Hook) -> Generator[None, None, None]:
    if before:
        before()
    try:
        yield
    except Exception:
        if on_exception:
            on_exception()
        raise
    else:
        if after:
            after()


@contextmanager
def _observe_latency(histogram: Histogram) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        histogram.observe(time.perf_counter() - start)

{%- endif %}
