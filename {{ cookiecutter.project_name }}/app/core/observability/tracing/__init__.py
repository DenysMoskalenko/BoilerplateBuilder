{%- if cookiecutter.use_otel_observability == "yes" %}
from app.core.observability.tracing.bootstrap import create_resource, EXCLUDED_URLS_REGEX, setup

__all__ = ('EXCLUDED_URLS_REGEX', 'create_resource', 'setup')
{%- endif %}
