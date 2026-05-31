{%- if cookiecutter.use_otel_observability == "yes" %}
from typing import TypedDict, Unpack

from fastapi import FastAPI
from pytest import MonkeyPatch

from app.core.config import get_settings, Settings
import app.core.observability.bootstrap as observability_bootstrap
from tests.unit.core.observability.mocks import ObservabilitySetupSpy


class SettingsOverrides(TypedDict, total=False):
    OBSERVABILITY_TRACING_ENABLED: bool
    OBSERVABILITY_METRICS_ENABLED: bool
    OBSERVABILITY_TRACING_OTLP_ENDPOINT: str | None


def build_settings(**overrides: Unpack[SettingsOverrides]) -> Settings:
    data = get_settings().model_dump()
    data.update(overrides)
    return Settings.model_validate(data)


def test_setup_configures_tracing_when_tracing_is_enabled(monkeypatch: MonkeyPatch) -> None:
    """Observability bootstrap starts tracing only when tracing is enabled."""
    app = FastAPI()
    settings = build_settings(
        OBSERVABILITY_TRACING_ENABLED=True,
        OBSERVABILITY_TRACING_OTLP_ENDPOINT='http://localhost:4317',
    )
    spy = ObservabilitySetupSpy()
    spy.install(monkeypatch)

    observability_bootstrap.setup(app=app, settings=settings)

    assert spy.tracing_was_configured is True


def test_setup_configures_metrics_when_metrics_are_enabled(monkeypatch: MonkeyPatch) -> None:
    """Observability bootstrap starts metrics only when metrics are enabled."""
    app = FastAPI()
    settings = build_settings(OBSERVABILITY_METRICS_ENABLED=True)
    spy = ObservabilitySetupSpy()
    spy.install(monkeypatch)

    observability_bootstrap.setup(app=app, settings=settings)

    assert spy.metrics_was_configured is True


def test_setup_skips_tracing_when_tracing_is_disabled(monkeypatch: MonkeyPatch) -> None:
    """Observability bootstrap does not start tracing when tracing is disabled."""
    app = FastAPI()
    settings = build_settings(OBSERVABILITY_TRACING_ENABLED=False)
    spy = ObservabilitySetupSpy()
    spy.install(monkeypatch)

    observability_bootstrap.setup(app=app, settings=settings)

    assert spy.tracing_was_configured is False


def test_setup_skips_metrics_when_metrics_are_disabled(monkeypatch: MonkeyPatch) -> None:
    """Observability bootstrap does not start metrics when metrics are disabled."""
    app = FastAPI()
    settings = build_settings(OBSERVABILITY_METRICS_ENABLED=False)
    spy = ObservabilitySetupSpy()
    spy.install(monkeypatch)

    observability_bootstrap.setup(app=app, settings=settings)

    assert spy.metrics_was_configured is False
{%- endif %}
