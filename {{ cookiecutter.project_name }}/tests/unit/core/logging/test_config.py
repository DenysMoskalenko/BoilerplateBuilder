from typing import Any

from pytest import MonkeyPatch

from app.core.logging import build_logging_config, config as logging_config_module, LogFormatType, LogLevel
from app.core.logging.config import DEFAULT_HANDLER_NAME


def test_build_logging_config_routes_uvicorn_loggers_to_console() -> None:
    """Logging config routes Uvicorn loggers through the application console handler."""
    config = build_logging_config(LogLevel.DEBUG, LogFormatType.JSON)

    assert {tuple(logger['handlers']) for logger in config['loggers'].values()} == {(DEFAULT_HANDLER_NAME,)}


def test_build_logging_config_prevents_uvicorn_log_propagation() -> None:
    """Logging config prevents duplicate Uvicorn records from propagating upward."""
    config = build_logging_config(LogLevel.DEBUG, LogFormatType.JSON)

    assert {logger['propagate'] for logger in config['loggers'].values()} == {False}


def test_build_logging_config_applies_log_level_to_uvicorn_loggers() -> None:
    """Logging config applies the configured level to Uvicorn loggers."""
    config = build_logging_config(LogLevel.DEBUG, LogFormatType.JSON)

    assert {logger['level'] for logger in config['loggers'].values()} == {LogLevel.DEBUG}


def test_configure_logging_applies_dict_config(monkeypatch: MonkeyPatch) -> None:
    """configure_logging applies the generated dictionary through logging.config."""
    calls: list[dict[str, Any]] = []

    def dict_config_spy(config: dict[str, Any]) -> None:
        calls.append(config)

    monkeypatch.setattr(logging_config_module, 'dictConfig', dict_config_spy)

    logging_config_module.configure_logging(LogLevel.INFO, LogFormatType.STDOUT)

    assert calls == [build_logging_config(LogLevel.INFO, LogFormatType.STDOUT)]
