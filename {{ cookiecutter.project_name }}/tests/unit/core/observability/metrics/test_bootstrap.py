{%- if cookiecutter.use_otel_observability == "yes" %}
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.core.observability.metrics.bootstrap as metrics_bootstrap


def test_setup_exposes_prometheus_metrics_endpoint() -> None:
    """Metrics setup exposes a Prometheus scrape endpoint."""
    app = FastAPI()

    metrics_bootstrap.setup(app=app)
    response = TestClient(app).get('/metrics/')

    assert response.status_code == 200
{%- endif %}
