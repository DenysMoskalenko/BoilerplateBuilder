{%- if cookiecutter.use_otel_observability == "yes" %}
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from types import TracebackType

from fastapi import FastAPI
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace.status import Status
from pytest import MonkeyPatch
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from pydantic_ai import InstrumentationSettings
{%- endif %}

from app.core.config import Settings
import app.core.observability.bootstrap as observability_bootstrap
import app.core.observability.tracing.bootstrap as tracing_bootstrap


@dataclass(slots=True)
class ObservabilitySetupSpy:
    tracing_settings: Settings | None = None
    metrics_app: FastAPI | None = None

    @property
    def tracing_was_configured(self) -> bool:
        return self.tracing_settings is not None

    @property
    def metrics_was_configured(self) -> bool:
        return self.metrics_app is not None

    def install(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr(observability_bootstrap.tracing, 'setup', self.setup_tracing)
        monkeypatch.setattr(observability_bootstrap.metrics, 'setup', self.setup_metrics)

    def setup_tracing(self, *, app: FastAPI, settings: Settings) -> None:
        self.tracing_settings = settings

    def setup_metrics(self, *, app: FastAPI) -> None:
        self.metrics_app = app


@dataclass(frozen=True, slots=True)
class SamplerSpy:
    ratio: float


@dataclass(frozen=True, slots=True)
class SpanExporterSpy:
    endpoint: str
    insecure: bool


@dataclass(frozen=True, slots=True)
class SpanProcessorSpy:
    span_exporter: SpanExporterSpy


@dataclass(slots=True)
class TracerProviderSpy:
    resource: Resource
    sampler: SamplerSpy
    span_processor: SpanProcessorSpy | None = None

    def add_span_processor(self, *, span_processor: SpanProcessorSpy) -> None:
        self.span_processor = span_processor


@dataclass(slots=True)
class LoggingInstrumentorSpy:
    setup: TracingBootstrapSpy

    def instrument(self, *, set_logging_format: bool) -> None:
        self.setup.logging_format_override_disabled = not set_logging_format


@dataclass(slots=True)
class FastAPIInstrumentorSpy:
    setup: TracingBootstrapSpy

    def instrument_app(self, app: FastAPI, *, exclude_spans: Sequence[str], excluded_urls: str) -> None:
        self.setup.fastapi_app = app
        self.setup.fastapi_exclude_spans = tuple(exclude_spans)
        self.setup.fastapi_excluded_urls = excluded_urls


{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
@dataclass(slots=True)
class SQLAlchemyInstrumentorSpy:
    setup: TracingBootstrapSpy

    def instrument(self) -> None:
        self.setup.sqlalchemy_was_instrumented = True


{%- endif %}
@dataclass(slots=True)
class TracingBootstrapSpy:
    logging_format_override_disabled: bool = False
    fastapi_app: FastAPI | None = None
    fastapi_exclude_spans: tuple[str, ...] = ()
    fastapi_excluded_urls: str | None = None
    sampler: SamplerSpy | None = None
    span_exporter: SpanExporterSpy | None = None
    span_processor: SpanProcessorSpy | None = None
    tracer_provider: TracerProviderSpy | None = None
    global_tracer_provider: TracerProviderSpy | None = None
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    sqlalchemy_was_instrumented: bool = False
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    agent_instrumentation: InstrumentationSettings | None = None
{%- endif %}

    @property
    def fastapi_was_instrumented(self) -> bool:
        return self.fastapi_app is not None

    @property
    def span_processor_was_attached(self) -> bool:
        return self.tracer_provider is not None and self.tracer_provider.span_processor is self.span_processor

    @property
    def global_provider_was_registered(self) -> bool:
        return self.global_tracer_provider is self.tracer_provider

{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    @property
    def agent_content_capture_disabled(self) -> bool:
        return (
            self.agent_instrumentation is not None
            and self.agent_instrumentation.include_content is False
            and self.agent_instrumentation.include_binary_content is False
        )

{%- endif %}
    def install(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setattr(tracing_bootstrap, 'LoggingInstrumentor', self.create_logging_instrumentor)
        monkeypatch.setattr(tracing_bootstrap, 'FastAPIInstrumentor', self.create_fastapi_instrumentor)
        monkeypatch.setattr(tracing_bootstrap, 'TraceIdRatioBased', self.create_sampler)
        monkeypatch.setattr(tracing_bootstrap, 'TracerProvider', self.create_tracer_provider)
        monkeypatch.setattr(tracing_bootstrap, 'OTLPSpanExporter', self.create_span_exporter)
        monkeypatch.setattr(tracing_bootstrap, 'BatchSpanProcessor', self.create_span_processor)
        monkeypatch.setattr(tracing_bootstrap.trace, 'set_tracer_provider', self.register_global_provider)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
        monkeypatch.setattr(tracing_bootstrap, 'SQLAlchemyInstrumentor', self.create_sqlalchemy_instrumentor)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
        monkeypatch.setattr(tracing_bootstrap.Agent, 'instrument_all', self.instrument_agent)
{%- endif %}

    def create_logging_instrumentor(self) -> LoggingInstrumentorSpy:
        return LoggingInstrumentorSpy(setup=self)

    def create_fastapi_instrumentor(self) -> FastAPIInstrumentorSpy:
        return FastAPIInstrumentorSpy(setup=self)

    def create_sampler(self, ratio: float) -> SamplerSpy:
        self.sampler = SamplerSpy(ratio=ratio)
        return self.sampler

    def create_tracer_provider(self, *, resource: Resource, sampler: SamplerSpy) -> TracerProviderSpy:
        self.tracer_provider = TracerProviderSpy(resource=resource, sampler=sampler)
        return self.tracer_provider

    def create_span_exporter(self, *, endpoint: str, insecure: bool) -> SpanExporterSpy:
        self.span_exporter = SpanExporterSpy(endpoint=endpoint, insecure=insecure)
        return self.span_exporter

    def create_span_processor(self, *, span_exporter: SpanExporterSpy) -> SpanProcessorSpy:
        self.span_processor = SpanProcessorSpy(span_exporter=span_exporter)
        return self.span_processor

    def register_global_provider(self, *, tracer_provider: TracerProviderSpy) -> None:
        self.global_tracer_provider = tracer_provider

{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    def create_sqlalchemy_instrumentor(self) -> SQLAlchemyInstrumentorSpy:
        return SQLAlchemyInstrumentorSpy(setup=self)

{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    def instrument_agent(self, *, instrument: InstrumentationSettings) -> None:
        self.agent_instrumentation = instrument

{%- endif %}

@dataclass(slots=True)
class SpanSpy:
    attributes: dict[str, str] = field(default_factory=dict)
    statuses: list[Status] = field(default_factory=list)

    @property
    def latest_status(self) -> Status:
        return self.statuses[-1]

    def set_attribute(self, key: str, value: str) -> None:
        self.attributes[key] = value

    def set_status(self, status: Status) -> None:
        self.statuses.append(status)


@dataclass(slots=True)
class SpanContextManagerSpy:
    span: SpanSpy

    def __enter__(self) -> SpanSpy:
        return self.span

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: TracebackType | None
    ) -> bool:
        return False


@dataclass(slots=True)
class TracerSpy:
    started_span_names: list[str] = field(default_factory=list)
    spans: list[SpanSpy] = field(default_factory=list)

    @property
    def latest_span(self) -> SpanSpy:
        return self.spans[-1]

    def start_as_current_span(self, name: str) -> SpanContextManagerSpy:
        span = SpanSpy()
        self.started_span_names.append(name)
        self.spans.append(span)
        return SpanContextManagerSpy(span=span)
{%- endif %}
