{%- if cookiecutter.use_otel_observability == "yes" %}
from .bootstrap import setup

__all__ = ('setup',)
{%- endif %}
