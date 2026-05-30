from enum import auto, StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

LOG_TIMESTAMP_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4}$'
LOG_TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
TimestampWithOffset = Annotated[
    str,
    Field(
        pattern=LOG_TIMESTAMP_PATTERN,
        examples=['2026-05-29T10:00:00+0000', '2026-05-29T12:30:00+0230'],
        description='ISO timestamp with numeric UTC offset',
    ),
]


class LogFormatType(StrEnum):
    JSON = auto()
    STDOUT = auto()


class StructuredLogRecord(BaseModel):
    timestamp: TimestampWithOffset
    logger_name: str
    level: str
    message: str
    stack_trace: str | None = None
    exception_type: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
