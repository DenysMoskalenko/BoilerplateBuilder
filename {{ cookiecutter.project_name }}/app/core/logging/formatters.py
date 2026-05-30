import logging
import sys
from typing import ClassVar

from app.core.logging.models import LOG_TIMESTAMP_FORMAT, StructuredLogRecord


def _get_otel_attribute(record: logging.LogRecord, key: str) -> str | None:
    value = record.__dict__.get(key)
    if not isinstance(value, str) or not value.strip('0'):
        return None
    return value


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        structured = StructuredLogRecord(
            timestamp=self.formatTime(record, LOG_TIMESTAMP_FORMAT),
            logger_name=record.name,
            level=record.levelname,
            message=record.getMessage(),
        )

        structured.trace_id = _get_otel_attribute(record=record, key='otelTraceID')
        structured.span_id = _get_otel_attribute(record=record, key='otelSpanID')

        exc_info = record.exc_info
        if exc_info:
            exc_type = exc_info[0]
            structured.stack_trace = self.formatException(exc_info)
            structured.exception_type = exc_type.__name__ if exc_type else None

        return structured.model_dump_json(exclude_none=True)


class ColorizedStdoutFormatter(logging.Formatter):
    _LEVEL_COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: '\x1b[36m',
        logging.INFO: '\x1b[32m',
        logging.WARNING: '\x1b[33m',
        logging.ERROR: '\x1b[31m',
        logging.CRITICAL: '\x1b[1;31m',
    }
    _RESET = '\x1b[0m'

    def __init__(self, fmt: str, datefmt: str, use_colors: bool) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        if self._should_use_colors():
            color = self._LEVEL_COLORS.get(record.levelno)
            if color:
                record.levelname = f'{color}{record.levelname}{self._RESET}'
        try:
            formatted = super().format(record)
        finally:
            record.levelname = original_levelname

        trace_suffix = self._build_trace_context_suffix(record=record)
        if not trace_suffix:
            return formatted
        return f'{formatted} {trace_suffix}'

    def _should_use_colors(self) -> bool:
        return self._use_colors and sys.stdout.isatty()

    @staticmethod
    def _build_trace_context_suffix(record: logging.LogRecord) -> str:
        entries = (
            ('trace_id', _get_otel_attribute(record=record, key='otelTraceID')),
            ('span_id', _get_otel_attribute(record=record, key='otelSpanID')),
        )
        parts = [f'{name}={value}' for name, value in entries if value]
        return ' '.join(parts)
