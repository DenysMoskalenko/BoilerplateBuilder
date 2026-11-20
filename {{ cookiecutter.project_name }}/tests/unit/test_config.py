from pathlib import Path
from typing import get_args

import pytest
from uvicorn.config import LOG_LEVELS

from app.core.config import Settings
from app.core.logging import LogLevel


def test_log_levels_are_ones_uvicorn_accepts() -> None:
    """LOG_LEVEL also sets uvicorn's level, and uvicorn refuses to start on one it does not know."""
    assert {level.lower() for level in get_args(LogLevel)} <= LOG_LEVELS.keys()


def test_settings_ignore_a_developers_env_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests read dist.env, whatever a developer keeps in `.env`."""
    (tmp_path / '.env').write_text('LOG_LEVEL=CRITICAL\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('LOG_LEVEL', raising=False)

    assert Settings().LOG_LEVEL == 'INFO'
