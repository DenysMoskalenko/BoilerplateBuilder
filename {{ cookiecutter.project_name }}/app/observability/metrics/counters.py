{%- if cookiecutter.use_otel_observability == "yes" %}
from prometheus_client import Counter
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

agent_requests_total = Counter(
    name='agent_requests_total',
    documentation='Total number of AI agent requests',
)
{%- endif %}
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

search_queries_total = Counter(
    name='search_queries_total',
    documentation='Total number of search/filter queries by resource',
    labelnames=('resource', 'has_filters'),
)
{%- endif %}
{%- if cookiecutter.project_type == "fastapi_slim" %}

http_business_requests_total = Counter(
    name='http_business_requests_total',
    documentation='Total business-level HTTP requests (extend with your own labels)',
)
{%- endif %}
{%- endif %}
