{%- if cookiecutter.use_otel_observability == "yes" %}
from typing import TypedDict, Unpack

import pytest

from app.core.config import get_settings, Settings


class SettingsOverrides(TypedDict, total=False):
    OBSERVABILITY_TRACING_ENABLED: bool
    OBSERVABILITY_METRICS_ENABLED: bool
    OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT: float
    OBSERVABILITY_TRACING_OTLP_ENDPOINT: str | None


def build_settings(**overrides: Unpack[SettingsOverrides]) -> Settings:
    data = get_settings().model_dump()
    for key in SettingsOverrides.__annotations__:
        data.pop(key, None)
    data.update(overrides)
    return Settings.model_validate(data)


def test_rejects_non_http_tracing_endpoint() -> None:
    """Settings reject OTLP endpoints that cannot be used by the HTTP URL type."""
    with pytest.raises(ValueError):
        build_settings(OBSERVABILITY_TRACING_OTLP_ENDPOINT='grpc://host:4317')


def test_tracing_endpoint_can_be_missing_when_tracing_is_disabled() -> None:
    """Settings allow an empty tracing endpoint while tracing is disabled."""
    settings = build_settings(OBSERVABILITY_TRACING_ENABLED=False, OBSERVABILITY_TRACING_OTLP_ENDPOINT=None)

    assert settings.OBSERVABILITY_TRACING_OTLP_ENDPOINT is None


def test_tracing_endpoint_is_required_when_tracing_is_enabled() -> None:
    """Settings require an exporter endpoint when tracing is enabled."""
    with pytest.raises(ValueError, match='OBSERVABILITY_TRACING_OTLP_ENDPOINT is required'):
        build_settings(OBSERVABILITY_TRACING_ENABLED=True, OBSERVABILITY_TRACING_OTLP_ENDPOINT=None)


@pytest.mark.parametrize('sample_rate', [-1.0, 101.0])
def test_tracing_sample_rate_rejects_out_of_range_percentages(sample_rate: float) -> None:
    """Settings reject sampling percentages outside the configured boundary."""
    with pytest.raises(ValueError):
        build_settings(OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT=sample_rate)
{%- endif %}
