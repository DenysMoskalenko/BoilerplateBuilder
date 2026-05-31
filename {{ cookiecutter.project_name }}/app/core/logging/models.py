from enum import auto, StrEnum

from pydantic import BaseModel

LOG_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class LogFormatType(StrEnum):
    JSON = auto()
    STDOUT = auto()


class StructuredLogRecord(BaseModel):
    timestamp: str
    logger_name: str
    level: str
    message: str
    stack_trace: str | None = None
    exception_type: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
