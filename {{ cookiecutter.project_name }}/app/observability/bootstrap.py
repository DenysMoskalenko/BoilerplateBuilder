{%- if cookiecutter.use_otel_observability == "yes" %}
import logging
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}

from fastapi import FastAPI
{%- endif %}
from opentelemetry import metrics, trace
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
from opentelemetry.exporter.prometheus import PrometheusMetricReader
{%- endif %}
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.semconv.attributes import service_attributes
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from prometheus_fastapi_instrumentator.metrics import default, latency
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
{%- endif %}

from app.core.config import Settings
from app.observability.logging_config import setup_json_logging

logger = logging.getLogger(__name__)


{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}


def setup_observability(app: FastAPI, settings: Settings) -> None:
{%- else %}


def setup_observability(settings: Settings) -> None:
{%- endif %}
    """Set up observability stack with logging, tracing, and metrics."""
    logger.info('Setting up observability...')

    if settings.OBSERVABILITY_LOGS_IN_JSON:
        setup_json_logging(settings.LOG_LEVEL)

{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
    _setup_tracing(app=app, settings=settings)
    _setup_metrics(app=app, settings=settings)
{%- else %}
    _setup_tracing(settings=settings)
    _setup_metrics(settings=settings)
{%- endif %}

    logger.info('Observability setup completed.')


{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}


def _setup_tracing(app: FastAPI, settings: Settings) -> None:
{%- else %}


def _setup_tracing(settings: Settings) -> None:
{%- endif %}
    """Configure distributed tracing with OpenTelemetry."""
    if not settings.OBSERVABILITY_TRACING_ENABLED:
        logger.info('Tracing is disabled. Skipping setup.')
        return

{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
    FastAPIInstrumentor().instrument_app(
        app, exclude_spans=['send', 'receive'], excluded_urls=r'^/metrics/?$,^/health-check/?$'
    )
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}
    SQLAlchemyInstrumentor().instrument()
{%- endif %}

    endpoint = settings.OBSERVABILITY_OTLP_GRPC_ENDPOINT
    resource = _create_resource(settings=settings)
    sampler = TraceIdRatioBased(settings.OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT / 100)

    provider = TracerProvider(resource=resource, sampler=sampler)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(tracer_provider=provider)

    logger.info(f'Tracing enabled and exporting to {endpoint}')




{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}


def _setup_metrics(app: FastAPI, settings: Settings) -> None:
{%- else %}


def _setup_metrics(settings: Settings) -> None:
{%- endif %}
    """Configure Prometheus metrics collection."""
    if not settings.OBSERVABILITY_METRICS_ENABLED:
        logger.info('Metrics are disabled. Skipping setup.')
        return

    resource = _create_resource(settings=settings)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
    provider = MeterProvider(resource=resource, metric_readers=[PrometheusMetricReader()])
{%- else %}
    provider = MeterProvider(resource=resource)
{%- endif %}
    metrics.set_meter_provider(meter_provider=provider)

{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
    instrumentator = PrometheusFastApiInstrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
    )
    instrumentator.add(default())
    instrumentator.add(latency())
    instrumentator.instrument(app)

    app.mount('/metrics/', make_asgi_app())
    logger.info('Prometheus metrics available at "/metrics/"')
{%- else %}
    logger.info('Metrics collection enabled.')
{%- endif %}


def _create_resource(settings: Settings) -> Resource:
    """Create OpenTelemetry resource with service metadata."""
    return Resource.create(
        {
            service_attributes.SERVICE_NAME: settings.PROJECT_NAME,
            service_attributes.SERVICE_VERSION: settings.PROJECT_VERSION,
        }
    )
{%- endif %}
