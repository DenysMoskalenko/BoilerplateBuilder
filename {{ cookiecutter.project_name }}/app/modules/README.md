# Modules

Business logic is organised **by feature**, one folder per feature under `app/modules/`.
Each module is a vertical slice (`routes` → `service` → `schemas`) so that everything
related to a feature lives together. Technical, cross-cutting code lives outside the
modules: in `app/core/` (config, logging,{% if cookiecutter.use_otel_observability == "yes" %} observability,{% endif %} base schemas, exceptions) and
`app/infrastructure/` ({% if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}db{% endif %}{% if cookiecutter.project_type == "fastapi_db_agent" %}, {% endif %}{% if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}llms{% endif %}).

Why the split: business code changes when a product requirement changes; technical code
changes when infrastructure changes. Keeping them apart means a feature change touches one
module folder, and an infrastructure change touches one infrastructure folder.

## Module layout

A module typically contains:

| File         | Responsibility                                             |
|--------------|------------------------------------------------------------|
| `routes.py`  | FastAPI router and endpoint handlers                       |
| `schemas.py` | Pydantic request/response and internal models             |
| `service.py` | Business logic; talks to the DB session and other services |
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
| `agents.py`  | (agent features) Pydantic AI agent construction and tools  |
| `prompts.py` | (agent features) system prompts and prompt text            |
{%- endif %}

This project ships `health_checks`{% if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}, `examples` (CRUD){% endif %}{% if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}, and `examples_agent` (AI){% endif %} as reference modules.
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

DB models do **not** live in the module. All SQLAlchemy models are centralised in
`app/infrastructure/db/models/` — a single source of truth that keeps Alembic
autogeneration and cross-model relationships simple.
{%- endif %}

## Start flat, grow into folders

Begin with flat files (`routes.py`, `schemas.py`, `service.py`). A concern becomes a
subpackage **only once it genuinely splits into 2+ files** — don't pre-split a module into
folders it doesn't need yet.
{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}

The `examples_agent` module is the reference for a justified split: its `schemas/` is a
subpackage because the HTTP contract and the agent/tool I/O are separate concerns:

- `schemas/schemas_api.py` — HTTP request/response models
- `schemas/schemas_agent.py` — agent dependencies and tool input/output models

Keep the descriptive filename prefix when splitting (`schemas_api.py`, not `api.py`) so
files stay unambiguous in search results and editor tabs.

## Subpackage imports — facade `__init__`

A subpackage exposes a **facade** `__init__.py` that re-exports its public symbols via
`__all__`. External callers import from the package root, not the deep path:

```python
# good — import from the package facade
from app.modules.examples_agent.schemas import ExampleAgentRequest

# avoid — reaching into the deep module from outside the package
from app.modules.examples_agent.schemas.schemas_api import ExampleAgentRequest
```

**Exception — internal sibling imports.** A module *inside* a subpackage imports its
siblings directly (`from .schemas_api import ExampleAgentRequest`), never through its own
package facade, to avoid circular-import fragility during package initialisation.
{%- else %}

When a subpackage does appear, give it a facade `__init__.py` that re-exports its public
symbols via `__all__` so external callers import from the package root rather than a deep
path. Inside that subpackage, modules import their siblings directly (e.g.
`from .other_module import Thing`) — never through their own package facade — to avoid
circular-import fragility during package initialisation.
{%- endif %}
