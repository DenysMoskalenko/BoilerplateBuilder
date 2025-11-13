{%- if cookiecutter.use_otel_observability == "yes" %}
from prometheus_client import Counter

{%- if cookiecutter.project_type == "fastapi_db" %}

examples_operations_total = Counter(
    name='examples_operations_total',
    documentation='Total number of example operations',
    labelnames=('operation', 'status'),
)
{%- elif cookiecutter.project_type == "cli_db" %}

database_operations_total = Counter(
    name='database_operations_total',
    documentation='Total number of database operations',
    labelnames=('operation',),
)
{%- else %}

# Example counter - replace with your actual business metrics
# No labelnames for simplicity - add them as needed for your use case
example_operations_total = Counter(
    name='example_operations_total',
    documentation='Example counter for demonstrating observability',
)
{%- endif %}
{%- endif %}
