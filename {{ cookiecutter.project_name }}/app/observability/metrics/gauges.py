{%- if cookiecutter.use_otel_observability == "yes" %}
from prometheus_client import Gauge

{%- if cookiecutter.project_type == "fastapi_db" %}

inflight_operations = Gauge(
    name='inflight_operations',
    documentation='Current in-flight operations',
    labelnames=('operation',),
)
{%- elif cookiecutter.project_type == "cli_db" %}

inflight_database_operations = Gauge(
    name='inflight_database_operations',
    documentation='Current in-flight database operations',
    labelnames=('operation',),
)
{%- else %}

# Example gauge - replace with your actual business metrics
# No labelnames for simplicity - add them as needed for your use case
example_inflight_operations = Gauge(
    name='example_inflight_operations',
    documentation='Example gauge for demonstrating observability',
)
{%- endif %}
{%- endif %}
