import logging
from logging.handlers import BufferingHandler

from app.core.logging import build_logging_config, configure_logging, LogFormatType


def test_uvicorn_records_reach_a_handler_on_the_root_logger() -> None:
    """A handler added to the root logger (an OTLP log exporter, Sentry) sees server errors too."""
    configure_logging('INFO', LogFormatType.STDOUT)
    root_handler = BufferingHandler(capacity=10)
    logging.getLogger().addHandler(root_handler)
    try:
        logging.getLogger('uvicorn.error').error('Exception in ASGI application')
    finally:
        logging.getLogger().removeHandler(root_handler)

    assert [record.getMessage() for record in root_handler.buffer] == ['Exception in ASGI application']


def test_build_logging_config_applies_log_level_to_uvicorn_loggers() -> None:
    """Logging config applies the configured level to Uvicorn loggers."""
    config = build_logging_config('DEBUG', LogFormatType.JSON)

    assert {logger['level'] for logger in config['loggers'].values()} == {'DEBUG'}
