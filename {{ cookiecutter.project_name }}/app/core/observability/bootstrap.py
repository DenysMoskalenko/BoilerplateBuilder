{%- if cookiecutter.use_otel_observability == "yes" %}
import logging

from fastapi import FastAPI

from app.core.config import Settings
from app.core.observability import metrics, tracing

logger = logging.getLogger(__name__)


def setup(app: FastAPI, settings: Settings) -> None:
    logger.info('Setting up observability...')

    if settings.OBSERVABILITY.tracing_enabled:
        tracing.setup(app=app, settings=settings)

    if settings.OBSERVABILITY.metrics_enabled:
        metrics.setup(app=app)

    logger.info('Observability setup completed.')
{%- endif %}
