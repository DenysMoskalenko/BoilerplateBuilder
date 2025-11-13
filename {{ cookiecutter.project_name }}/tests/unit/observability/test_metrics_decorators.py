{%- if cookiecutter.use_otel_observability == "yes" %}
import pytest

from app.observability.metrics.primitives.decorators import increment_after, track_inflight


class Counter:
    """Mock counter for testing."""

    def __init__(self) -> None:
        self.n = 0

    def inc(self) -> None:
        self.n += 1

    def dec(self) -> None:
        self.n -= 1


# ---- Sync variants ----


def test_track_inflight_sync_ok() -> None:
    """Test track_inflight decorator with sync function that completes successfully."""
    g = Counter()

    @track_inflight(g)
    def f() -> int:
        return 42

    assert f() == 42
    assert g.n == 0


def test_track_inflight_sync_exception() -> None:
    """Test track_inflight decorator with sync function that raises an exception."""
    g = Counter()

    @track_inflight(g)
    def boom() -> None:
        raise RuntimeError('x')

    with pytest.raises(RuntimeError):
        boom()
    assert g.n == 0


def test_increment_after_sync_default_success_only_no_inc_on_error() -> None:
    """Test increment_after decorator does not increment on error by default."""
    c = Counter()

    @increment_after(c)
    def boom() -> None:
        raise RuntimeError('y')

    with pytest.raises(RuntimeError):
        boom()
    assert c.n == 0


def test_increment_after_sync_increments_on_success() -> None:
    """Test increment_after decorator increments on successful completion."""
    c = Counter()

    @increment_after(c)
    def ok() -> int:
        return 1

    assert ok() == 1
    assert c.n == 1


def test_increment_after_sync_inc_even_on_error_when_flag_false() -> None:
    """Test increment_after decorator increments even on error when success_only=False."""
    c = Counter()

    @increment_after(c, success_only=False)
    def boom() -> None:
        raise RuntimeError('y')

    with pytest.raises(RuntimeError):
        boom()
    assert c.n == 1


# ---- Async variants ----


@pytest.mark.asyncio
async def test_track_inflight_async_ok() -> None:
    """Test track_inflight decorator with async function that completes successfully."""
    g = Counter()

    @track_inflight(g)
    async def f() -> int:
        return 42

    assert await f() == 42
    assert g.n == 0


@pytest.mark.asyncio
async def test_track_inflight_async_exception() -> None:
    """Test track_inflight decorator with async function that raises an exception."""
    g = Counter()

    @track_inflight(g)
    async def boom() -> None:
        raise RuntimeError('x')

    with pytest.raises(RuntimeError):
        await boom()
    assert g.n == 0


@pytest.mark.asyncio
async def test_increment_after_async_default_success_only_no_inc_on_error() -> None:
    """Test increment_after decorator does not increment on error by default (async)."""
    c = Counter()

    @increment_after(c)
    async def boom() -> None:
        raise RuntimeError('y')

    with pytest.raises(RuntimeError):
        await boom()
    assert c.n == 0


@pytest.mark.asyncio
async def test_increment_after_async_increments_on_success() -> None:
    """Test increment_after decorator increments on successful completion (async)."""
    c = Counter()

    @increment_after(c)
    async def ok() -> int:
        return 2

    assert await ok() == 2
    assert c.n == 1


@pytest.mark.asyncio
async def test_increment_after_async_inc_even_on_error_when_flag_false() -> None:
    """Test increment_after decorator increments even on error when success_only=False (async)."""
    c = Counter()

    @increment_after(c, success_only=False)
    async def boom() -> None:
        raise RuntimeError('y')

    with pytest.raises(RuntimeError):
        await boom()
    assert c.n == 1
{%- endif %}
