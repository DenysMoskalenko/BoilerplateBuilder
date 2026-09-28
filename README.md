# BoilerplateBuilder

Cookiecutter template for production-ready FastAPI applications. Generates a fully configured project with linting, testing, Docker, CI/CD, and optional database and AI agent support, plus telemetry enabled by default.

## Quick Start

```bash
uv tool run cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder
```

Or install cookiecutter and run directly:

```bash
pip install cookiecutter
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder
```

## Project Types

| Type | Description |
|------|-------------|
| **`fastapi_db_agent`** | FastAPI + PostgreSQL + AI agent (pydantic-ai). The full setup. |
| **`fastapi_db`** | FastAPI + PostgreSQL. CRUD API with migrations, pagination, filtering. |
| **`fastapi_agent`** | FastAPI + AI agent. No database, just an LLM-powered endpoint. |
| **`fastapi_slim`** | Minimal FastAPI. Health checks, Docker, tests, and default telemetry. |

All types share: Python 3.11–3.14, uv, Ruff + ty, pytest, Docker, Makefile, pre-commit (via prek), and optional GitHub Actions.

### What each type adds

**Database types** (`fastapi_db`, `fastapi_db_agent`):
- PostgreSQL with async SQLAlchemy 2.0 and Alembic migrations
- docker-compose for local Postgres
- Testcontainers for isolated DB tests
- Example model with CRUD service, pagination, filtering, and search

**Agent types** (`fastapi_agent`, `fastapi_db_agent`):
- AI agent built with [pydantic-ai](https://github.com/pydantic/pydantic-ai)
- OpenAI and AWS Bedrock provider support
- Example agent with tool usage and conversation API
- Agent test mocks for deterministic testing

**Observability** (enabled by default for every type; opt-outs below):
- OpenTelemetry tracing, Prometheus metrics, structured JSON logging
- Custom metric decorators (`@track_inflight`, `@increment_after`, `@increment_on_error`, `@track_latency`)
- Local dev stack: Grafana, Tempo, Prometheus, Loki, OTEL Collector, Grafana Alloy

## Generated Project Structure

```
your-project/
├── app/
│   ├── main.py
│   ├── router.py                      # Aggregates domain routers (create_router)
│   ├── core/                          # Config, logging, observability, exceptions, schemas
│   ├── infrastructure/                # Technical adapters
│   │   ├── db/
│   │   │   └── models/                # All SQLAlchemy models (db types)
│   │   └── llms/                      # LLM provider config (agent types)
│   └── domains/                       # Business logic, one vertical slice per feature
│       ├── README.md                  # Domain conventions
│       ├── health_checks/             # Liveness & readiness probes (routes + schemas + service)
│       ├── examples/                  # Example CRUD feature (db types)
│       └── examples_agent/            # Example AI agent feature (agent types)
│           ├── agents.py              # Agent construction & tools
│           ├── prompts.py
│           └── schemas/               # API contract + agent/tool I/O (facade subpackage)
├── tests/
│   ├── api/                           # API integration tests
│   ├── unit/                          # Unit tests
│   └── mocks/                         # Agent test mocks (agent types)
├── migrations/                        # Alembic (db types)
├── local_telemetry/                   # Grafana stack (if enabled)
├── Dockerfile
├── docker-compose.yaml                # Postgres / telemetry services
├── Makefile
├── pyproject.toml
└── dist.env                           # Example environment variables
```

## Non-Interactive Generation

```bash
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder \
  --no-input \
  project_name="MyAPI" \
  project_type="fastapi_db" \
  python_version="3.14"
```

All options with defaults:

| Option | Default | Values |
|--------|---------|--------|
| `extract_to_current_dir` | `Create New` | `Create New`, `Extract Here` |
| `project_name` | `MyProject` | any string |
| `project_type` | `fastapi_db_agent` | `fastapi_db_agent`, `fastapi_db`, `fastapi_agent`, `fastapi_slim` |
| `python_version` | `3.14` | `3.14`, `3.13`, `3.12`, `3.11` |
| `use_github_actions` | `yes` | `yes`, `no` |
| `initialize_git` | `yes` | `yes`, `no` |
| `use_otel_observability` | `yes` | `yes`, `no` |
| `generate_local_otel_stack` | `yes` | `yes`, `no` (requires `use_otel_observability=yes`) |

To disable telemetry, pass `use_otel_observability=no generate_local_otel_stack=no`: the local stack defaults to `yes`,
and `no/yes` is rejected.

Docker is required for DB tests and to run the local telemetry stack, not to generate it.

## After Generation

```bash
cd your-project

# Dependencies are installed automatically during generation
# If not, run:
uv sync

# Run the app on the host (disable tracing in .env if no collector is running)
make run
# http://localhost:8000/docs

# Lint & test
make lint
make test
```

For database types:

```bash
make up-dependencies    # Start Postgres
make migrate            # Apply migrations
make run
```

With the local stack, `docker compose up -d --build` runs the API, telemetry, and Postgres together instead.

## Development Commands (Generated Project)

```bash
make run                # Start the application
make lint               # Format + lint (ruff)
make check              # Lint + typecheck + tests
make test               # Run tests
make test-coverage      # Tests with coverage report
make up-dependencies    # Start Postgres (db types)
make migrate            # Apply all migrations (db types)
make migration MSG="…"  # Create new migration (db types)
```

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Package manager**: [uv](https://github.com/astral-sh/uv)
- **Linter/formatter**: [Ruff](https://github.com/astral-sh/ruff)
- **Type checker**: [ty](https://github.com/astral-sh/ty)
- **Testing**: [pytest](https://docs.pytest.org/) with async support, [testcontainers](https://testcontainers-python.readthedocs.io/)
- **Database**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + [Alembic](https://alembic.sqlalchemy.org/)
- **AI agents**: [pydantic-ai](https://github.com/pydantic/pydantic-ai) with OpenAI and AWS Bedrock
- **Observability**: [OpenTelemetry](https://opentelemetry.io/), Prometheus, Grafana, Tempo, Loki, Grafana Alloy
- **CI/CD**: GitHub Actions with matrix testing across Python 3.11–3.14

## Contributing

1. Fork and create a feature branch
2. Make changes in `{{ cookiecutter.project_name }}/` and `hooks/`
3. Test all project types:
   ```bash
   for pt in fastapi_slim fastapi_db fastapi_agent fastapi_db_agent; do
     cookiecutter . --no-input project_name="Test" project_type="$pt" && rm -rf Test
   done
   ```
4. Submit a pull request

## License

MIT — see [LICENSE](LICENSE).
