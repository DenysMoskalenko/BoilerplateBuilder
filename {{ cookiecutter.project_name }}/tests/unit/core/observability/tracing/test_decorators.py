{%- if cookiecutter.use_otel_observability == "yes" %}
from opentelemetry.trace.status import StatusCode
import pytest
from pytest import MonkeyPatch

import app.core.observability.tracing.primitives.decorators as tracing_decorators
from tests.unit.core.observability.mocks import TracerSpy


def install_tracer_spy(monkeypatch: MonkeyPatch) -> TracerSpy:
    tracer = TracerSpy()
    monkeypatch.setattr(tracing_decorators, 'tracer', tracer)
    return tracer


def test_trace_returns_sync_result(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator preserves the wrapped synchronous function result."""
    install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    def sample(value: int) -> int:
        return value + 1

    assert sample(1) == 2


def test_trace_uses_default_span_name(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator names spans from the wrapped function by default."""
    tracer = install_tracer_spy(monkeypatch)

    def sample() -> None:
        return None

    tracing_decorators.trace(sample)()

    assert tracer.started_span_names == [f'{sample.__module__}.{sample.__qualname__}']


def test_trace_records_function_name(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator records the wrapped function name as a span attribute."""
    tracer = install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    def sample() -> None:
        return None

    sample()

    assert tracer.latest_span.attributes == {'code.function': 'sample'}


def test_trace_marks_sync_success_as_ok(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator marks successful synchronous calls as OK."""
    tracer = install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    def sample() -> None:
        return None

    sample()

    assert tracer.latest_span.latest_status.status_code is StatusCode.OK


def test_trace_reraises_sync_failures(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator re-raises synchronous failures from the wrapped function."""
    install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        sample()


def test_trace_marks_sync_failures_as_error(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator marks failed synchronous calls as ERROR."""
    tracer = install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        sample()

    assert (tracer.latest_span.latest_status.status_code, tracer.latest_span.latest_status.description) == (
        StatusCode.ERROR,
        'boom',
    )


async def test_trace_returns_async_result(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator preserves the wrapped asynchronous function result."""
    install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    async def sample() -> str:
        return 'ok'

    assert await sample() == 'ok'


async def test_trace_uses_custom_async_span_name(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator uses explicit span names for asynchronous functions."""
    tracer = install_tracer_spy(monkeypatch)

    @tracing_decorators.trace(span_name='custom.span')
    async def sample() -> None:
        return None

    await sample()

    assert tracer.started_span_names == ['custom.span']


async def test_trace_marks_async_success_as_ok(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator marks successful asynchronous calls as OK."""
    tracer = install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    async def sample() -> None:
        return None

    await sample()

    assert tracer.latest_span.latest_status.status_code is StatusCode.OK


async def test_trace_marks_async_failures_as_error(monkeypatch: MonkeyPatch) -> None:
    """Trace decorator marks failed asynchronous calls as ERROR."""
    tracer = install_tracer_spy(monkeypatch)

    @tracing_decorators.trace
    async def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        await sample()

    assert (tracer.latest_span.latest_status.status_code, tracer.latest_span.latest_status.description) == (
        StatusCode.ERROR,
        'boom',
    )
{%- endif %}
