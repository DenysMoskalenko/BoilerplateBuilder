{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import asyncio
from pathlib import Path
from typing import Any, cast

from pydantic import SecretStr, ValidationError
import pytest
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import DatabaseSettings
from app.domains.health_checks.service import check_database_status


def test_url_keeps_credentials_out_of_the_url_structure() -> None:
    """Credentials holding URL syntax round-trip instead of reading as host or path."""
    settings = DatabaseSettings(host='db', port=5432, user='svc@ops', password=SecretStr('p@ss/w:rd%40?#'), name='app')

    url = make_url(settings.url.unicode_string())

    assert (url.username, url.password, url.host, url.database) == ('svc@ops', 'p@ss/w:rd%40?#', 'db', 'app')


def test_invalid_host_keeps_the_password_out_of_the_error() -> None:
    """`PostgresDsn.build` reports a rejected value with the whole URL as its input."""
    settings = DatabaseSettings(host='bad host', port=5432, user='svc', password=SecretStr('secret'), name='app')

    with pytest.raises(ValueError) as exc_info:
        settings.url.unicode_string()

    assert 'input_value' not in str(exc_info.value)


def test_missing_variable_keeps_raw_values_out_of_the_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A startup failure on a missing variable must not print the password it already loaded."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('DATABASE_PASSWORD', 'hunter2')
    monkeypatch.delenv('DATABASE_USER', raising=False)

    with pytest.raises(ValidationError) as exc_info:
        DatabaseSettings()  # type: ignore[ty:missing-argument]

    assert 'input_value' not in str(exc_info.value)


async def test_database_check_reports_down_when_the_query_outlives_the_timeout() -> None:
    """A hung query answers readiness with DOWN instead of waiting on TCP retries."""

    class HangingSession:
        async def execute(self, *args: Any, **kwargs: Any) -> None:
            await asyncio.Event().wait()

    status = await check_database_status(cast(AsyncSession, HangingSession()), timeout_seconds=0.01)

    assert status == 'DOWN'
{%- endif %}
