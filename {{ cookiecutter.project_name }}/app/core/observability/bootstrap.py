{%- if cookiecutter.use_otel_observability == "yes" %}
import logging

from fastapi import FastAPI

from app.core.config import Settings
from app.core.observability import metrics, tracing

logger = logging.getLogger(__name__)


def setup(app: FastAPI, settings: Settings) -> None:
    logger.info('Setting up observability...')

    if settings.OBSERVABILITY_TRACING_ENABLED:
        tracing.setup(app=app, settings=settings)

    if settings.OBSERVABILITY_METRICS_ENABLED:
        metrics.setup(app=app)

    logger.info('Observability setup completed.')
{%- endif %}
