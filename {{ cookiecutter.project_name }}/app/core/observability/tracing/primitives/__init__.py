{%- if cookiecutter.use_otel_observability == "yes" -%}
from app.core.observability.tracing.primitives.decorators import trace

__all__ = ['trace']
{%- endif %}
