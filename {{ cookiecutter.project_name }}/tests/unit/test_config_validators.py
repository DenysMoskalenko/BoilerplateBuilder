{%- if cookiecutter.use_otel_observability == "yes" %}
from pathlib import Path
from typing import TypedDict, Unpack

from pydantic import ValidationError
import pytest

from app.core.config import get_settings, ObservabilitySettings, Settings


class SettingsOverrides(TypedDict, total=False):
    tracing_enabled: bool
    metrics_enabled: bool
    tracing_sample_rate_percent: float
    tracing_otlp_endpoint: str | None


def build_settings(**overrides: Unpack[SettingsOverrides]) -> Settings:
    data = get_settings().model_dump()
    data['OBSERVABILITY'] = overrides
    return Settings.model_validate(data)


def test_accepts_grpc_tracing_endpoint() -> None:
    """Settings accept grpc:// endpoints for OTLP export over gRPC."""
    settings = build_settings(tracing_otlp_endpoint='grpc://host:4317')

    assert settings.OBSERVABILITY.tracing_otlp_endpoint is not None
    assert settings.OBSERVABILITY.tracing_otlp_endpoint.scheme == 'grpc'


def test_rejects_unsupported_scheme_tracing_endpoint() -> None:
    """Settings reject OTLP endpoints whose scheme no exporter transport can use."""
    with pytest.raises(ValueError):
        build_settings(tracing_otlp_endpoint='ftp://host:4317')


def test_tracing_endpoint_can_be_missing_when_tracing_is_disabled() -> None:
    """Settings allow an empty tracing endpoint while tracing is disabled."""
    settings = build_settings(tracing_enabled=False, tracing_otlp_endpoint=None)

    assert settings.OBSERVABILITY.tracing_otlp_endpoint is None


def test_tracing_endpoint_is_required_when_tracing_is_enabled() -> None:
    """Settings require an exporter endpoint when tracing is enabled."""
    with pytest.raises(ValueError, match='OBSERVABILITY_TRACING_OTLP_ENDPOINT is required'):
        build_settings(tracing_enabled=True, tracing_otlp_endpoint=None)


def test_settings_error_keeps_env_file_values_out_of_the_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Every class receives the whole `.env`, so its errors must not print another class's secret."""
    (tmp_path / '.env').write_text('AWS_SECRET_ACCESS_KEY=hunter2\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('OBSERVABILITY_TRACING_ENABLED', 'true')
    monkeypatch.delenv('OBSERVABILITY_TRACING_OTLP_ENDPOINT', raising=False)

    with pytest.raises(ValidationError) as exc_info:
        ObservabilitySettings()

    assert 'input_value' not in str(exc_info.value)


@pytest.mark.parametrize('sample_rate', [-1.0, 101.0])
def test_tracing_sample_rate_rejects_out_of_range_percentages(sample_rate: float) -> None:
    """Settings reject sampling percentages outside the configured boundary."""
    with pytest.raises(ValueError):
        build_settings(tracing_sample_rate_percent=sample_rate)
{%- endif %}
