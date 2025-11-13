{%- if cookiecutter.use_otel_observability == "yes" %}
import logging
import sys
from functools import lru_cache
from typing import Any, Literal

from opentelemetry.instrumentation.logging import LoggingInstrumentor
from pydantic import BaseModel
from uvicorn.config import LOGGING_CONFIG

from app.core.config import get_settings


class LogEntry(BaseModel):
    """Structured log entry with OpenTelemetry trace correlation."""

    message: str
    timestamp: str
    name: str
    level: str
    trace_id: str | None = None
    span_id: str | None = None
    exception_type: str | None = None
    stack_trace: str | None = None


class LogsJSONFormatter(logging.Formatter):
    """JSON formatter that includes OpenTelemetry trace and span IDs."""

    def format(self, record: logging.LogRecord) -> str:
        return LogEntry(
            timestamp=self.formatTime(record, '%Y-%m-%dT%H:%M:%S%z'),
            name=record.name,
            level=record.levelname,
            trace_id=getattr(record, 'otelTraceID', None),
            span_id=getattr(record, 'otelSpanID', None),
            message=record.getMessage(),
            stack_trace=self.formatException(record.exc_info) if record.exc_info else None,
            exception_type=record.exc_info[0].__name__ if record.exc_info else None,
        ).model_dump_json(exclude_none=True)


def setup_json_logging(level: Literal['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'] = 'INFO') -> None:
    """Configure JSON logging with OTel correlation fields."""
    LoggingInstrumentor().instrument(set_logging_format=True)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(LogsJSONFormatter())

    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)


@lru_cache
def get_uvicorn_logging_config() -> tuple[dict[str, Any] | None, str]:
    """Return uvicorn logging config (JSON or default) and log level."""
    settings = get_settings()
    if not settings.OBSERVABILITY_LOGS_IN_JSON:
        return None, settings.LOG_LEVEL.lower()

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                '()': 'app.observability.logging_config.LogsJSONFormatter',
            },
        },
        'handlers': {
            'default': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
            'access': {
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'uvicorn': {
                'handlers': ['default'],
                'level': settings.LOG_LEVEL,
                'propagate': False,
            },
            'uvicorn.error': {
                'level': settings.LOG_LEVEL,
            },
            'uvicorn.access': {
                'handlers': ['access'],
                'level': settings.LOG_LEVEL,
                'propagate': False,
            },
        },
        'root': {
            'level': settings.LOG_LEVEL,
            'handlers': ['default'],
        },
    }, settings.LOG_LEVEL.lower()
{%- endif %}
