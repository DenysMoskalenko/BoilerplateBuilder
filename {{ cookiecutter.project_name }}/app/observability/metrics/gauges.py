{%- if cookiecutter.use_otel_observability == "yes" %}
from prometheus_client import Gauge
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

agent_inflight_requests = Gauge(
    name='agent_inflight_requests',
    documentation='Number of AI agent requests currently being processed',
)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

database_connections_active = Gauge(
    name='database_connections_active',
    documentation='Number of active database connections',
)
{%- endif %}
{%- if cookiecutter.project_type == "fastapi_slim" %}

app_info = Gauge(
    name='app_info',
    documentation='Application info gauge (extend with your own labels)',
    labelnames=('version',),
)
{%- endif %}
{%- endif %}
