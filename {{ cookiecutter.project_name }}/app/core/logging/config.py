from enum import StrEnum
from logging.config import dictConfig
from typing import Any

from app.core.logging.models import LOG_TIMESTAMP_FORMAT, LogFormatType

STDOUT_LOG_FORMAT_TEMPLATE = '[%(asctime)s] %(levelname)s %(name)s %(message)s'
DEFAULT_HANDLER_NAME = 'console'
ROOT_LOGGER_NAME = 'root'
UVICORN_LOGGER_NAMES = ('uvicorn', 'uvicorn.error', 'uvicorn.access')


class LogLevel(StrEnum):
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'
    DEBUG = 'DEBUG'
    NOTSET = 'NOTSET'


def build_logging_config(log_level: LogLevel, format_type: LogFormatType) -> dict[str, Any]:
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            LogFormatType.STDOUT: {
                '()': 'app.core.logging.formatters.ColorizedStdoutFormatter',
                'format': STDOUT_LOG_FORMAT_TEMPLATE,
                'datefmt': LOG_TIMESTAMP_FORMAT,
                'use_colors': True,
            },
            LogFormatType.JSON: {'()': 'app.core.logging.formatters.StructuredJsonFormatter'},
        },
        'handlers': {
            DEFAULT_HANDLER_NAME: {
                'class': 'logging.StreamHandler',
                'formatter': format_type,
                'stream': 'ext://sys.stdout',
            }
        },
        ROOT_LOGGER_NAME: {'level': log_level, 'handlers': [DEFAULT_HANDLER_NAME]},
        'loggers': {
            logger_name: {'level': log_level, 'handlers': [DEFAULT_HANDLER_NAME], 'propagate': False}
            for logger_name in UVICORN_LOGGER_NAMES
        },
    }


def configure_logging(log_level: LogLevel, format_type: LogFormatType) -> None:
    dictConfig(build_logging_config(log_level, format_type))
