{%- if cookiecutter.use_otel_observability == "yes" %}
import logging

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.semconv.attributes import service_attributes
from prometheus_client import make_asgi_app
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
{%- endif %}
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from app.core.config import Settings

logger = logging.getLogger(__name__)


def setup_observability(app: FastAPI, settings: Settings) -> None:
    """Set up observability stack with logging, tracing, and metrics."""
    logger.info('Setting up observability...')

    _setup_tracing(settings=settings)
    _setup_metrics(app=app, settings=settings)
    _setup_instrumentors(app=app)

    logger.info('Observability setup completed.')


def _setup_tracing(settings: Settings) -> None:
    """Configure distributed tracing with OpenTelemetry."""
    if not settings.OBSERVABILITY_TRACING_ENABLED:
        logger.info('Tracing is disabled. Skipping setup.')
        return

    endpoint = settings.OBSERVABILITY_OTLP_GRPC_ENDPOINT
    resource = _create_resource(settings=settings)
    sampler = TraceIdRatioBased(settings.OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT / 100)

    provider = TracerProvider(resource=resource, sampler=sampler)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True)))
    trace.set_tracer_provider(tracer_provider=provider)

    logger.info(f'Tracing enabled and exporting to {endpoint}')


def _setup_metrics(app: FastAPI, settings: Settings) -> None:
    """Configure Prometheus metrics collection."""
    if not settings.OBSERVABILITY_METRICS_ENABLED:
        logger.info('Metrics are disabled. Skipping setup.')
        return

    resource = _create_resource(settings=settings)
    provider = MeterProvider(resource=resource, metric_readers=[PrometheusMetricReader()])
    metrics.set_meter_provider(meter_provider=provider)

    app.mount('/metrics/', make_asgi_app())
    logger.info('Metrics available at "/metrics/"')
    logger.info('Metrics collection enabled.')


def _setup_instrumentors(app: FastAPI) -> None:
    FastAPIInstrumentor().instrument_app(
        app, exclude_spans=['send', 'receive'], excluded_urls='/health/live,/health/ready,/metrics/'
    )
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    SQLAlchemyInstrumentor().instrument()
{%- endif %}
    LoggingInstrumentor().instrument()


def _create_resource(settings: Settings) -> Resource:
    """Create OpenTelemetry resource with service metadata."""
    return Resource.create(
        {
            service_attributes.SERVICE_NAME: settings.PROJECT_NAME,
            service_attributes.SERVICE_VERSION: settings.PROJECT_VERSION,
        }
    )
{%- endif %}
