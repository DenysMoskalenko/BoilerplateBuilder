{%- if cookiecutter.use_otel_observability == "yes" %}
from app.core.observability.bootstrap import setup

__all__ = ('setup',)
{%- endif %}
