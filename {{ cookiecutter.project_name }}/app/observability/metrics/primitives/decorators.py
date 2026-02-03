{%- if cookiecutter.use_otel_observability == "yes" %}
import asyncio
from functools import wraps
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar, cast, overload

P = ParamSpec('P')
T = TypeVar('T')


def track_inflight(gauge_or_child: Any) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to increase/decrease a Prometheus Gauge around function execution.

    Accepts either a Gauge (unlabeled) or a labeled child, e.g.:
      @track_inflight(gauges.inflight_operations.labels('create_example'))
      async def handler(...): ...
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        return _wrap_with_hooks(func, before=gauge_or_child.inc, after=gauge_or_child.dec)

    return decorator


def increment_after(counter_or_child: Any, *, success_only: bool = True) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to increment a Prometheus Counter after function execution.

    Parameters:
      counter_or_child: either a Counter (unlabeled) or a labeled child, e.g.:
          @increment_after(counters.examples_operations_total.labels('create', 'success'))
          async def handler(...): ...
      success_only: if True (default), increment only when the wrapped function
        completes successfully; if False, increment even when it raises.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        return _wrap_with_hooks(func, before=None, after=counter_or_child.inc, after_on_success_only=success_only)

    return decorator


@overload
def _wrap_with_hooks(
    func: Callable[P, Awaitable[T]],
    *,
    before: Callable[[], None] | None,
    after: Callable[[], None] | None,
    after_on_success_only: bool = False,
) -> Callable[P, Awaitable[T]]: ...


@overload
def _wrap_with_hooks(
    func: Callable[P, T],
    *,
    before: Callable[[], None] | None,
    after: Callable[[], None] | None,
    after_on_success_only: bool = False,
) -> Callable[P, T]: ...


def _wrap_with_hooks(
    func: Callable[P, T] | Callable[P, Awaitable[T]],
    *,
    before: Callable[[], None] | None,
    after: Callable[[], None] | None,
    after_on_success_only: bool = False,
) -> Callable[P, Any]:
    """Return a wrapper that runs before()/after() around func, supports sync/async.

    If ``after_on_success_only`` is True, the ``after`` hook runs only when the
    wrapped function completes without raising. Otherwise it always runs.
    """

    if asyncio.iscoroutinefunction(func):
        func_async = cast(Callable[P, Awaitable[T]], func)

        @wraps(func)
        async def a_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if before:
                before()
            _ok = False
            try:
                result = await func_async(*args, **kwargs)
                _ok = True
                return result
            finally:
                if after and (not after_on_success_only or _ok):
                    after()

        return a_wrapper

    func_sync = cast(Callable[P, T], func)

    @wraps(func)
    def s_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if before:
            before()
        _ok = False
        try:
            result = func_sync(*args, **kwargs)
            _ok = True
            return result
        finally:
            if after and (not after_on_success_only or _ok):
                after()

    return s_wrapper
{%- endif %}
