{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
import asyncio
from pathlib import Path
from typing import Any, cast

from pydantic import SecretStr, ValidationError
import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.health_checks.service import check_database_status
from app.core.config import DatabaseSettings, get_settings
from app.infrastructure.db.database import async_engine


def build_database_settings(host: str = 'db', name: str = 'app') -> DatabaseSettings:
    return DatabaseSettings(host=host, port=5432, user='svc', password=SecretStr('secret'), name=name)


def test_url_keeps_credentials_out_of_the_url_structure() -> None:
    """Credentials holding URL syntax round-trip instead of reading as host or path."""
    settings = DatabaseSettings(host='db', port=5432, user='svc@ops', password=SecretStr('p@ss/w:rd%40?#'), name='app')

    url = make_url(settings.url.unicode_string())

    assert (url.username, url.password, url.host, url.database) == ('svc@ops', 'p@ss/w:rd%40?#', 'db', 'app')


def test_url_accepts_bracketed_ipv6_host() -> None:
    """A bracketed IPv6 literal is the one host allowed to contain colons."""
    assert make_url(build_database_settings(host='[::1]').url.unicode_string()).host == '::1'


@pytest.mark.parametrize(
    'value', ['h@other', 'db?sslmode=disable', 'a/b', 'a:5432', '[not-ipv6]', '[fe80::1%eth0]', 'bücher']
)
@pytest.mark.parametrize('field', ['host', 'name'])
def test_rejects_url_syntax_in_unquoted_parts(field: str, value: str) -> None:
    """Host and name are not quoted, so URL syntax in them would compose a different URL."""
    with pytest.raises(ValidationError, match='bracketed IPv6 literal'):
        build_database_settings(**{field: value})


def test_missing_variable_keeps_raw_values_out_of_the_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A startup failure on a missing variable must not print the password it already loaded."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('DATABASE_PASSWORD', 'hunter2')
    monkeypatch.delenv('DATABASE_USER', raising=False)

    with pytest.raises(ValidationError) as exc_info:
        DatabaseSettings()  # type: ignore[ty:missing-argument]

    assert 'input_value' not in str(exc_info.value)


async def test_engine_applies_the_connect_and_statement_timeouts() -> None:
    """Every pooled connection starts with the configured timeouts."""
    database = get_settings().DATABASE
    engine = async_engine()

    async with engine.connect() as connection:
        statement_timeout_ms = await connection.scalar(
            text("SELECT setting FROM pg_settings WHERE name = 'statement_timeout'")
        )
        raw_connection = await connection.get_raw_connection()
        parameters = cast(Any, raw_connection.driver_connection).info.get_parameters()
    await engine.dispose()

    assert int(statement_timeout_ms) == database.statement_timeout_seconds * 1000
    assert int(parameters['connect_timeout']) == database.connect_timeout_seconds


async def test_database_check_reports_down_when_the_query_outlives_the_timeout() -> None:
    """A hung query answers readiness with DOWN instead of waiting on TCP retries."""

    class HangingSession:
        async def execute(self, *args: Any, **kwargs: Any) -> None:
            await asyncio.Event().wait()

    status = await check_database_status(cast(AsyncSession, HangingSession()), timeout_seconds=0.01)

    assert status == 'DOWN'
{%- endif %}
