from dataclasses import dataclass

from pytest import MonkeyPatch

import app.main as app_main
from app.core.logging import LogFormatType


@dataclass(frozen=True, slots=True)
class AppSettings:
    PROJECT_NAME: str = 'svc'
    PROJECT_VERSION: str = '1.2.3'
    LOG_LEVEL: str = 'DEBUG'
    LOG_FORMAT: LogFormatType = LogFormatType.JSON
    ROOT_PATH: str = ''


def test_create_app_configures_logging_from_settings(monkeypatch: MonkeyPatch) -> None:
    """The app factory applies template logging for uvicorn factory launches."""
    settings = AppSettings()
    calls: list[tuple[str, LogFormatType]] = []

    def record_configure_logging(log_level: str, format_type: LogFormatType) -> None:
        calls.append((log_level, format_type))

    monkeypatch.setattr(app_main, 'get_settings', lambda: settings)
    monkeypatch.setattr(app_main, 'configure_logging', record_configure_logging, raising=False)
{%- if cookiecutter.use_otel_observability == "yes" %}
    monkeypatch.setattr(app_main.observability, 'setup', lambda *, app, settings: None)
{%- endif %}

    app_main.create_app()

    assert calls == [(settings.LOG_LEVEL, settings.LOG_FORMAT)]
