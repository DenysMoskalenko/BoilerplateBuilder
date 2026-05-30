{%- if cookiecutter.use_otel_observability == "yes" %}
import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
{%- endif %}
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.semconv.attributes import service_attributes
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from pydantic_ai import Agent, InstrumentationSettings
{%- endif %}

from app.core.config import Settings

logger = logging.getLogger(__name__)

# The ASGI instrumentation checks excluded_urls against the full URL, not only the path.
EXCLUDED_URLS_REGEX = r'^(?:https?://[^/]+)?/(metrics|health(?:/(?:live|ready))?)/?$'


def create_resource(settings: Settings) -> Resource:
    return Resource.create(
        {
            service_attributes.SERVICE_NAME: settings.PROJECT_NAME,
            service_attributes.SERVICE_VERSION: settings.PROJECT_VERSION,
        }
    )


def setup(app: FastAPI, settings: Settings) -> None:
    LoggingInstrumentor().instrument(set_logging_format=False)
    FastAPIInstrumentor().instrument_app(app, exclude_spans=['send', 'receive'], excluded_urls=EXCLUDED_URLS_REGEX)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
    SQLAlchemyInstrumentor().instrument()
{%- endif %}

    endpoint = settings.OBSERVABILITY_TRACING_OTLP_ENDPOINT
    if endpoint is None:
        raise ValueError('OBSERVABILITY_TRACING_OTLP_ENDPOINT is required when tracing is enabled')

    sampler = TraceIdRatioBased(settings.OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT / 100)
    provider = TracerProvider(resource=create_resource(settings=settings), sampler=sampler)
    span_exporter = OTLPSpanExporter(endpoint=endpoint.encoded_string(), insecure=endpoint.scheme != 'https')
    span_processor = BatchSpanProcessor(span_exporter=span_exporter)
    provider.add_span_processor(span_processor=span_processor)
    trace.set_tracer_provider(tracer_provider=provider)
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
    Agent.instrument_all(instrument=InstrumentationSettings(include_content=False, include_binary_content=False))
{%- endif %}

    logger.info(f'Tracing enabled and exporting to {endpoint}')
{%- endif %}
