{%- if cookiecutter.use_otel_observability == "yes" %}
from typing import TypedDict, Unpack

from fastapi import FastAPI
from opentelemetry.semconv.attributes import service_attributes
import pytest
from pytest import MonkeyPatch

from app.core.config import get_settings, Settings
import app.core.observability.tracing.bootstrap as tracing_bootstrap
from tests.unit.core.observability.mocks import SpanExporterSpy, TracingBootstrapSpy


class SettingsOverrides(TypedDict, total=False):
    PROJECT_NAME: str
    PROJECT_VERSION: str
    OBSERVABILITY_TRACING_ENABLED: bool
    OBSERVABILITY_METRICS_ENABLED: bool
    OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT: float
    OBSERVABILITY_TRACING_OTLP_ENDPOINT: str | None


def build_settings(**overrides: Unpack[SettingsOverrides]) -> Settings:
    data = get_settings().model_dump()
    data.update(overrides)
    return Settings.model_validate(data)


def setup_tracing(monkeypatch: MonkeyPatch, **overrides: Unpack[SettingsOverrides]) -> TracingBootstrapSpy:
    settings_overrides: SettingsOverrides = {'OBSERVABILITY_TRACING_OTLP_ENDPOINT': 'http://localhost:4317'}
    settings_overrides.update(overrides)
    settings = build_settings(**settings_overrides)
    spy = TracingBootstrapSpy()
    spy.install(monkeypatch)

    tracing_bootstrap.setup(app=FastAPI(), settings=settings)

    return spy


def test_create_resource_sets_service_name() -> None:
    """Trace resources carry the configured service name."""
    settings = build_settings(PROJECT_NAME='svc')

    resource = tracing_bootstrap.create_resource(settings=settings)

    assert resource.attributes[service_attributes.SERVICE_NAME] == 'svc'


def test_create_resource_sets_service_version() -> None:
    """Trace resources carry the configured service version."""
    settings = build_settings(PROJECT_VERSION='1.2.3')

    resource = tracing_bootstrap.create_resource(settings=settings)

    assert resource.attributes[service_attributes.SERVICE_VERSION] == '1.2.3'


def test_setup_keeps_existing_logging_format(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup enriches logs without replacing the configured formatter."""
    spy = setup_tracing(monkeypatch)

    assert spy.logging_format_override_disabled is True


def test_setup_instruments_fastapi(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup instruments the FastAPI app."""
    spy = setup_tracing(monkeypatch)

    assert spy.fastapi_was_instrumented is True


def test_setup_excludes_noise_endpoints_from_fastapi_spans(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup excludes health and metrics endpoints from request spans."""
    spy = setup_tracing(monkeypatch)

    assert spy.fastapi_excluded_urls == tracing_bootstrap.EXCLUDED_URLS_REGEX


def test_setup_converts_sampling_percent_to_ratio(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup converts percentage sampling config to OpenTelemetry ratio."""
    spy = setup_tracing(monkeypatch, OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT=25.0)

    assert spy.sampler is not None and spy.sampler.ratio == 0.25


def test_setup_uses_secure_exporter_for_https_endpoint(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup keeps the OTLP exporter secure for HTTPS endpoints."""
    spy = setup_tracing(monkeypatch, OBSERVABILITY_TRACING_OTLP_ENDPOINT='https://collector.internal:4317')

    assert spy.span_exporter == SpanExporterSpy(endpoint='https://collector.internal:4317/', insecure=False)


def test_setup_attaches_span_processor_to_provider(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup connects the OTLP exporter pipeline to the tracer provider."""
    spy = setup_tracing(monkeypatch)

    assert spy.span_processor_was_attached is True


def test_setup_registers_tracer_provider_globally(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup publishes the configured tracer provider globally."""
    spy = setup_tracing(monkeypatch)

    assert spy.global_provider_was_registered is True


def test_setup_requires_endpoint(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup fails loudly when validation was bypassed and endpoint is missing."""
    spy = TracingBootstrapSpy()
    spy.install(monkeypatch)
    settings = get_settings().model_copy(update={'OBSERVABILITY_TRACING_OTLP_ENDPOINT': None})

    with pytest.raises(ValueError, match='OBSERVABILITY_TRACING_OTLP_ENDPOINT is required'):
        tracing_bootstrap.setup(app=FastAPI(), settings=settings)


{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
def test_setup_instruments_sqlalchemy(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup instruments SQLAlchemy when database support is generated."""
    spy = setup_tracing(monkeypatch)

    assert spy.sqlalchemy_was_instrumented is True


{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
def test_setup_disables_agent_content_capture(monkeypatch: MonkeyPatch) -> None:
    """Tracing setup disables agent content capture to avoid leaking prompt data."""
    spy = setup_tracing(monkeypatch)

    assert spy.agent_content_capture_disabled is True
{%- endif %}
{%- endif %}
