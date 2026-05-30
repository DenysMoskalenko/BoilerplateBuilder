{%- if cookiecutter.use_otel_observability == "yes" -%}
from app.core.observability.metrics.primitives.decorators import (
    increment_after,
    increment_on_error,
    track_inflight,
    track_latency,
)
from app.core.observability.metrics.primitives.enums import Section

__all__ = ['Section', 'increment_after', 'increment_on_error', 'track_inflight', 'track_latency']
{%- endif %}
