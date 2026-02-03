import logging

from pydantic import BaseModel


class LogEntry(BaseModel):
    """Structured log entry with OpenTelemetry trace correlation."""

    timestamp: str
    name: str
    level: str
    trace_id: str | None = None
    span_id: str | None = None
    message: str
    exception_type: str | None = None
    stack_trace: str | None = None


class LogsJSONFormatter(logging.Formatter):
    """JSON formatter that includes OpenTelemetry trace and span IDs."""

    def format(self, record: logging.LogRecord) -> str:
        return LogEntry(
            timestamp=self.formatTime(record, '%Y-%m-%dT%H:%M:%S%z'),
            name=record.name,
            level=record.levelname,
            trace_id=self._clean_zero(getattr(record, 'otelTraceID', None)),
            span_id=self._clean_zero(getattr(record, 'otelSpanID', None)),
            message=record.getMessage(),
            stack_trace=self.formatException(record.exc_info) if record.exc_info else None,
            exception_type=record.exc_info[0].__name__ if (record.exc_info and record.exc_info[0]) else None,
        ).model_dump_json(exclude_none=True)

    @staticmethod
    def _clean_zero(value: str | None) -> str | None:
        """
        Normalize OTEL trace/span IDs. Uvicorn/OpenTelemetry uses the string '0' when a trace_id or span_id is absent.
        """
        return None if value == '0' else value
