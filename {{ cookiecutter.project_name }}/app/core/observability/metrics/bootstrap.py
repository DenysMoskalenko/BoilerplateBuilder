{%- if cookiecutter.use_otel_observability == "yes" %}
import logging

from fastapi import FastAPI
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from prometheus_fastapi_instrumentator.metrics import default

_logger = logging.getLogger(__name__)


def setup(app: FastAPI) -> None:
    instrumentator = PrometheusFastApiInstrumentator(should_group_status_codes=True, should_ignore_untemplated=True)
    instrumentator.add(default())
    instrumentator.instrument(app)

    app.mount('/metrics/', make_asgi_app())
    _logger.info('Prometheus metrics available at "/metrics/"')
{%- endif %}
