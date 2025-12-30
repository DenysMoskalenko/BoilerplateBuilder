{%- if cookiecutter.use_otel_observability == "yes" %}
import pytest

from app.core.config import Settings, get_settings


def test_invalid_otlp_scheme() -> None:
    """Test that invalid OTLP scheme raises validation error."""
    base_config = get_settings().model_dump()
    base_config.update({
        'OBSERVABILITY_TRACING_ENABLED': False,
        'OBSERVABILITY_OTLP_GRPC_ENDPOINT': 'http://host:4317',
    })

    with pytest.raises(ValueError, match='OTLP_GRPC_ENDPOINT must use the grpc:// scheme'):
        Settings(**base_config)


def test_invalid_otlp_no_host() -> None:
    """Test that OTLP endpoint without host raises validation error."""
    base_config = get_settings().model_dump()
    base_config.update({
        'OBSERVABILITY_TRACING_ENABLED': False,
        'OBSERVABILITY_OTLP_GRPC_ENDPOINT': 'grpc://:4317',
    })

    with pytest.raises(ValueError, match='OTLP_GRPC_ENDPOINT must include a hostname'):
        Settings(**base_config)


def test_invalid_otlp_no_port() -> None:
    """Test that OTLP endpoint without port raises validation error."""
    base_config = get_settings().model_dump()
    base_config.update({
        'OBSERVABILITY_TRACING_ENABLED': False,
        'OBSERVABILITY_OTLP_GRPC_ENDPOINT': 'grpc://host',
    })

    with pytest.raises(ValueError, match='OTLP_GRPC_ENDPOINT must include a port'):
        Settings(**base_config)


def test_tracing_enabled_without_endpoint() -> None:
    """Test that tracing enabled without endpoint raises validation error."""
    base_config = get_settings().model_dump()
    base_config.update({
        'OBSERVABILITY_TRACING_ENABLED': True,
        'OBSERVABILITY_OTLP_GRPC_ENDPOINT': None,
    })

    with pytest.raises(ValueError, match='but no OBSERVABILITY_OTLP_GRPC_ENDPOINT is configured'):
        Settings(**base_config)


def test_valid_observability_config() -> None:
    """Test that valid observability configuration is accepted."""
    base_config = get_settings().model_dump()
    base_config.update({
        'OBSERVABILITY_TRACING_ENABLED': True,
        'OBSERVABILITY_LOGS_IN_JSON': True,
        'OBSERVABILITY_OTLP_GRPC_ENDPOINT': 'grpc://localhost:4317',
    })

    settings = Settings(**base_config)
    assert settings.OBSERVABILITY_TRACING_ENABLED is True
    assert settings.OBSERVABILITY_LOGS_IN_JSON is True
    assert settings.OBSERVABILITY_OTLP_GRPC_ENDPOINT == 'grpc://localhost:4317'


def test_observability_disabled() -> None:
    """Test that observability can be disabled."""
    base_config = get_settings().model_dump()
    base_config.update({
        'OBSERVABILITY_TRACING_ENABLED': False,
        'OBSERVABILITY_METRICS_ENABLED': False,
    })

    settings = Settings(**base_config)
    assert settings.OBSERVABILITY_TRACING_ENABLED is False
    assert settings.OBSERVABILITY_METRICS_ENABLED is False
{%- endif %}
