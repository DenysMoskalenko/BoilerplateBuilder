{%- if cookiecutter.use_otel_observability == "yes" %}
from functools import lru_cache
from typing import Any

from app.core.config import get_settings


@lru_cache
def get_uvicorn_logging_config() -> tuple[dict[str, Any] | None, str]:
    """
    Return a logging config derived from Uvicorn's default configuration, with the root logger routed through JSON
    or text console handlers.
    """
    settings = get_settings()
    default_formatter = 'json' if settings.OBSERVABILITY_LOGS_IN_JSON else 'default'
    access_formatter = 'json' if settings.OBSERVABILITY_LOGS_IN_JSON else 'access'

    config: dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                '()': 'uvicorn.logging.DefaultFormatter',
                'fmt': '%(levelprefix)s [%(asctime)s] %(name)s %(message)s',
                'use_colors': True,
            },
            'access': {
                '()': 'uvicorn.logging.AccessFormatter',
                'fmt': '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
            'json': {
                '()': 'app.observability.logging.formatters.LogsJSONFormatter',
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': default_formatter,
                'stream': 'ext://sys.stderr',
            },
            'access': {
                'class': 'logging.StreamHandler',
                'formatter': access_formatter,
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'uvicorn': {
                'handlers': ['default'],
                'level': settings.LOG_LEVEL,
                'propagate': False,
            },
            'uvicorn.access': {
                'handlers': ['access'],
                'level': settings.LOG_LEVEL,
                'propagate': False,
            },
        },
        'root': {
            'handlers': ['default'],
            'level': settings.LOG_LEVEL,
        },
    }

    return config, settings.LOG_LEVEL.lower()
{%- endif %}
