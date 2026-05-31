import json
import logging
from types import TracebackType
from typing import TypeAlias

from pytest import MonkeyPatch

from app.core.logging.formatters import ColorizedStdoutFormatter, StructuredJsonFormatter

TraceContextValue: TypeAlias = str | int | None


def build_log_record(
    level: int = logging.INFO,
    message: str = 'hello',
    exc_info: tuple[type[BaseException], BaseException, TracebackType | None] | None = None,
    otel_trace_id: TraceContextValue = None,
    otel_span_id: TraceContextValue = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name='app.test', level=level, pathname=__file__, lineno=1, msg=message, args=(), exc_info=exc_info
    )
    if otel_trace_id is not None:
        record.otelTraceID = otel_trace_id
    if otel_span_id is not None:
        record.otelSpanID = otel_span_id
    return record


def capture_exc_info() -> tuple[type[BaseException], BaseException, TracebackType | None]:
    try:
        raise RuntimeError('boom')
    except RuntimeError as exc:
        return (RuntimeError, exc, exc.__traceback__)


def test_structured_json_formatter_serializes_base_fields() -> None:
    """Structured formatter emits the stable fields every log record needs."""
    formatter = StructuredJsonFormatter()
    record = build_log_record()

    payload = json.loads(formatter.format(record))

    assert payload == {
        'timestamp': payload['timestamp'],
        'logger_name': 'app.test',
        'level': 'INFO',
        'message': 'hello',
    }


def test_structured_json_formatter_adds_trace_context() -> None:
    """Structured formatter includes OpenTelemetry trace identifiers when present."""
    formatter = StructuredJsonFormatter()
    record = build_log_record(otel_trace_id='abc123', otel_span_id='def456')

    payload = json.loads(formatter.format(record))

    assert {'trace_id': payload['trace_id'], 'span_id': payload['span_id']} == {
        'trace_id': 'abc123',
        'span_id': 'def456',
    }


def test_structured_json_formatter_ignores_empty_trace_context() -> None:
    """Structured formatter does not emit placeholder trace identifiers."""
    formatter = StructuredJsonFormatter()
    record = build_log_record(otel_trace_id='000000')

    payload = json.loads(formatter.format(record))

    assert 'trace_id' not in payload


def test_structured_json_formatter_includes_exception_type() -> None:
    """Structured formatter records the exception type for failed log events."""
    formatter = StructuredJsonFormatter()
    record = build_log_record(level=logging.ERROR, exc_info=capture_exc_info())

    payload = json.loads(formatter.format(record))

    assert payload['exception_type'] == 'RuntimeError'


def test_structured_json_formatter_includes_stack_trace() -> None:
    """Structured formatter records the stack trace for failed log events."""
    formatter = StructuredJsonFormatter()
    record = build_log_record(level=logging.ERROR, exc_info=capture_exc_info())

    payload = json.loads(formatter.format(record))

    assert 'RuntimeError: boom' in payload['stack_trace']


def test_colorized_stdout_formatter_colorizes_tty_levelname(monkeypatch: MonkeyPatch) -> None:
    """Stdout formatter colorizes level names when color output is enabled on a TTY."""
    formatter = ColorizedStdoutFormatter(
        fmt='%(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', use_colors=True
    )
    record = build_log_record(level=logging.ERROR)
    monkeypatch.setattr('sys.stdout.isatty', lambda: True)

    assert formatter.format(record) == '\x1b[31mERROR\x1b[0m hello'


def test_colorized_stdout_formatter_restores_record_levelname(monkeypatch: MonkeyPatch) -> None:
    """Stdout formatter does not leave ANSI codes on the reused log record."""
    formatter = ColorizedStdoutFormatter(
        fmt='%(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', use_colors=True
    )
    record = build_log_record(level=logging.ERROR)
    monkeypatch.setattr('sys.stdout.isatty', lambda: True)

    formatter.format(record)

    assert record.levelname == 'ERROR'


def test_colorized_stdout_formatter_appends_trace_context() -> None:
    """Stdout formatter appends trace identifiers to plain log lines."""
    formatter = ColorizedStdoutFormatter(
        fmt='%(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', use_colors=False
    )
    record = build_log_record(otel_trace_id='abc123', otel_span_id='def456')

    assert formatter.format(record) == 'INFO hello trace_id=abc123 span_id=def456'


def test_colorized_stdout_formatter_leaves_plain_output_without_tty(monkeypatch: MonkeyPatch) -> None:
    """Stdout formatter leaves non-TTY output uncolored."""
    formatter = ColorizedStdoutFormatter(
        fmt='%(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', use_colors=True
    )
    record = build_log_record()
    monkeypatch.setattr('sys.stdout.isatty', lambda: False)

    assert formatter.format(record) == 'INFO hello'
