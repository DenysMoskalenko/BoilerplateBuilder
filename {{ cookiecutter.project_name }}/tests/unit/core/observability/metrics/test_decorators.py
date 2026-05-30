{%- if cookiecutter.use_otel_observability == "yes" %}
import warnings

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
import pytest
from pytest import MonkeyPatch

import app.core.observability.metrics.primitives.decorators as metrics_decorators


def build_gauge(name: str) -> Gauge:
    return Gauge(name, 'Test gauge', registry=CollectorRegistry())


def build_counter(name: str) -> Counter:
    return Counter(name, 'Test counter', registry=CollectorRegistry())


def build_histogram(name: str) -> Histogram:
    return Histogram(name, 'Test histogram', registry=CollectorRegistry())


def get_metric_value(metric: Gauge | Counter | Histogram, sample_name: str) -> float:
    for metric_family in metric.collect():
        for sample in metric_family.samples:
            if sample.name == sample_name:
                return float(sample.value)
    raise AssertionError(f'Metric sample {sample_name!r} not found')


def test_track_inflight_increments_sync_gauge_during_call() -> None:
    """Inflight tracking increments a synchronous gauge while the call is running."""
    gauge = build_gauge('test_track_inflight_sync_increment')
    observed_inflight_values: list[float] = []

    @metrics_decorators.track_inflight(gauge)
    def sample() -> None:
        observed_inflight_values.append(get_metric_value(gauge, 'test_track_inflight_sync_increment'))

    sample()

    assert observed_inflight_values == [1.0]


def test_track_inflight_decrements_sync_gauge_after_call() -> None:
    """Inflight tracking decrements a synchronous gauge after the call finishes."""
    gauge = build_gauge('test_track_inflight_sync_decrement')

    @metrics_decorators.track_inflight(gauge)
    def sample() -> None:
        return None

    sample()

    assert get_metric_value(gauge, 'test_track_inflight_sync_decrement') == 0.0


async def test_track_inflight_increments_async_gauge_during_call() -> None:
    """Inflight tracking increments an asynchronous gauge while the call is running."""
    gauge = build_gauge('test_track_inflight_async_increment')
    observed_inflight_values: list[float] = []

    @metrics_decorators.track_inflight(gauge)
    async def sample() -> None:
        observed_inflight_values.append(get_metric_value(gauge, 'test_track_inflight_async_increment'))

    await sample()

    assert observed_inflight_values == [1.0]


async def test_track_inflight_decrements_async_gauge_after_failure() -> None:
    """Inflight tracking decrements asynchronous gauges after failed calls."""
    gauge = build_gauge('test_track_inflight_async_error')

    @metrics_decorators.track_inflight(gauge)
    async def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        await sample()

    assert get_metric_value(gauge, 'test_track_inflight_async_error') == 0.0


def test_track_inflight_supports_async_functions_without_warnings() -> None:
    """Inflight tracking supports asynchronous functions without warnings."""
    gauge = build_gauge('test_track_inflight_async_warning')

    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)

        @metrics_decorators.track_inflight(gauge)
        async def sample() -> str:
            return 'ok'

    assert callable(sample)


def test_increment_after_counts_sync_successes_by_default() -> None:
    """Completion counters increment after successful synchronous calls."""
    counter = build_counter('test_increment_after_success')

    @metrics_decorators.increment_after(counter)
    def sample() -> None:
        return None

    sample()

    assert get_metric_value(counter, 'test_increment_after_success_total') == 1.0


def test_increment_after_skips_failed_calls_when_success_only_is_enabled() -> None:
    """Completion counters skip failed calls when success-only mode is enabled."""
    counter = build_counter('test_increment_after_error_skip')

    @metrics_decorators.increment_after(counter)
    def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        sample()

    assert get_metric_value(counter, 'test_increment_after_error_skip_total') == 0.0


def test_increment_after_can_count_failed_calls_when_success_only_is_disabled() -> None:
    """Completion counters count failed calls when success-only mode is disabled."""
    counter = build_counter('test_increment_after_error_count')

    @metrics_decorators.increment_after(counter, success_only=False)
    def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        sample()

    assert get_metric_value(counter, 'test_increment_after_error_count_total') == 1.0


async def test_increment_on_error_counts_async_failures() -> None:
    """Error counters increment after asynchronous failures."""
    counter = build_counter('test_increment_on_error_async')

    @metrics_decorators.increment_on_error(counter)
    async def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        await sample()

    assert get_metric_value(counter, 'test_increment_on_error_async_total') == 1.0


def test_increment_on_error_counts_sync_failures() -> None:
    """Error counters increment after synchronous failures."""
    counter = build_counter('test_increment_on_error_sync')

    @metrics_decorators.increment_on_error(counter)
    def sample() -> None:
        raise RuntimeError('boom')

    with pytest.raises(RuntimeError, match='boom'):
        sample()

    assert get_metric_value(counter, 'test_increment_on_error_sync_total') == 1.0


def test_track_latency_records_sync_observation_count(monkeypatch: MonkeyPatch) -> None:
    """Latency tracking records one synchronous histogram observation per call."""
    histogram = build_histogram('test_track_latency_sync_count')
    perf_counter_values = iter((10.0, 10.25))
    monkeypatch.setattr(metrics_decorators.time, 'perf_counter', lambda: next(perf_counter_values))

    @metrics_decorators.track_latency(histogram)
    def sample() -> None:
        return None

    sample()

    assert get_metric_value(histogram, 'test_track_latency_sync_count_count') == 1.0


def test_track_latency_records_sync_duration(monkeypatch: MonkeyPatch) -> None:
    """Latency tracking records synchronous execution duration."""
    histogram = build_histogram('test_track_latency_sync_sum')
    perf_counter_values = iter((10.0, 10.25))
    monkeypatch.setattr(metrics_decorators.time, 'perf_counter', lambda: next(perf_counter_values))

    @metrics_decorators.track_latency(histogram)
    def sample() -> None:
        return None

    sample()

    assert get_metric_value(histogram, 'test_track_latency_sync_sum_sum') == 0.25


async def test_track_latency_records_async_observation_count(monkeypatch: MonkeyPatch) -> None:
    """Latency tracking records one asynchronous histogram observation per call."""
    histogram = build_histogram('test_track_latency_async_count')
    perf_counter_values = iter((20.0, 20.5))
    monkeypatch.setattr(metrics_decorators.time, 'perf_counter', lambda: next(perf_counter_values))

    @metrics_decorators.track_latency(histogram)
    async def sample() -> None:
        return None

    await sample()

    assert get_metric_value(histogram, 'test_track_latency_async_count_count') == 1.0


async def test_track_latency_records_async_duration(monkeypatch: MonkeyPatch) -> None:
    """Latency tracking records asynchronous execution duration."""
    histogram = build_histogram('test_track_latency_async_sum')
    perf_counter_values = iter((20.0, 20.5))
    monkeypatch.setattr(metrics_decorators.time, 'perf_counter', lambda: next(perf_counter_values))

    @metrics_decorators.track_latency(histogram)
    async def sample() -> None:
        return None

    await sample()

    assert get_metric_value(histogram, 'test_track_latency_async_sum_sum') == 0.5
{%- endif %}
