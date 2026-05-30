{%- if cookiecutter.use_otel_observability == "yes" -%}
from .decorators import trace

__all__ = ['trace']
{%- endif %}
