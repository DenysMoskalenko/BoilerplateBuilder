# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

BoilerplateBuilder is a **Cookiecutter template** that generates production-ready FastAPI projects — it is not itself a runnable application. You edit *template source*, then generate a project to run or test it. Two distinct trees:

- **Template root** (`hooks/`, `cookiecutter.json`, `scripts/`, `.github/`, this file): the generator.
- **`{{ cookiecutter.project_name }}/`**: the source for generated projects. Every file here may contain Jinja2 (`{%- if cookiecutter.project_type in [...] %}`, `{{ cookiecutter.x }}`). Edit these with placeholders intact — never render the template and edit the output.

There is no root `pyproject.toml` or `Makefile`; the `Makefile`, the ruff/ty/pytest config, and all app code live under `{{ cookiecutter.project_name }}/` and apply only to generated projects. The root repo itself is linted only by the generic hooks in `.pre-commit-config.yaml`.

See `AGENTS.md` for contributor-facing guidelines (commit/PR conventions, etc.).

## Generation options (`cookiecutter.json`)

`project_type` selects the feature set; the rest are orthogonal toggles:

| Option | Values | Notes |
|--------|--------|-------|
| `project_type` | `fastapi_db_agent` / `fastapi_db` / `fastapi_agent` / `fastapi_slim` | `db_agent` = everything; `slim` = health checks + Docker + tests only |
| `use_otel_observability` | `no` / `yes` | adds `app/core/observability` + OTEL/Prometheus deps |
| `generate_local_otel_stack` | `no` / `yes` | **requires `use_otel_observability=yes`** (else the post-gen hook exits 1 and no project is created) |
| `use_pre_commit`, `use_github_actions`, `initialize_git` | `yes` / `no` | |
| `python_version` | `3.13` / `3.12` / `3.11` | |
| `extract_to_current_dir` | `Create New` / `Extract Here` | "Extract Here" merges output into the parent dir, for adding the template to an existing repo |

Hooks derive two boolean axes from `project_type`: `IS_DB` (`fastapi_db`, `fastapi_db_agent`) and `IS_AGENT` (`fastapi_agent`, `fastapi_db_agent`).

## How conditional generation works (read before editing template files)

Three mechanisms decide what a generated project contains. One feature change usually touches more than one:

1. **In-file Jinja** — `{%- if cookiecutter.project_type in [...] %}` blocks gate imports and code *within* a file. Guard added code so that **every** project type still produces valid, lint-clean Python (an unused import fails ruff `F`/`ANN`). See the top of `app/core/config.py`: the `{% set is_agent %}` block picks the exact `typing` imports per type precisely to avoid unused-import errors.
2. **Jinja in path names** — files/dirs whose entire name is a conditional, e.g. `{%- if cookiecutter.project_type in ["fastapi_db","fastapi_db_agent"] %}alembic.ini{%- endif %}` and everything under `migrations/`. When the condition is false the name renders empty and the path is skipped.
3. **Post-gen deletion** — `hooks/post_gen_project.py::remove_empty_files()` deletes whole paths not needed for the chosen type (per-type `paths_to_remove` lists) plus the observability / local-telemetry trees. **If you add, move, or rename files for a given type, update these lists.**

After cookiecutter renders, `hooks/post_gen_project.py` runs this pipeline (order matters): validate observability config → extract-to-current-dir → remove unneeded files → write `.env` from `dist.env` → `uv lock && uv sync` (+ `pre-commit install`) → `ruff format` + `ruff check --fix` → blank out whitespace-only `.py` files → strip leading blank lines → `git init` + initial commit → print next steps. Keep this hook idempotent and cross-platform (Python 3.11+).

## Working on the template

```bash
# Generate one type to inspect output (skip git/dep side effects for a quick look)
cookiecutter . --no-input project_type=fastapi_db initialize_git=no use_pre_commit=no

# Canonical validation: generate each type, then uv sync + make lint + make typecheck + make test inside each
python -m scripts.template_smoke_test                                  # all types, python 3.12, no otel
python -m scripts.template_smoke_test --project-types fastapi_slim --keep-builds
python -m scripts.template_smoke_test --use-otel yes --local-otel-stack yes
```

`scripts/template_smoke_test.py` is the real test harness (generated output goes under `.template-builds/`). It needs `cookiecutter`, `uv`, `make`, and **Docker** (db types use testcontainers). Mirror it for any non-trivial change.

A template change is correct only when **every affected `project_type` still generates, lints, type-checks, and tests green** — and for observability work, across all four `use_otel_observability`/`generate_local_otel_stack` pairs: `yes/yes`, `yes/no`, `no/no`, and `no/yes` (which must fail early and create nothing). This is exactly what `.github/workflows/test-templates.yml` enforces: a `4 types × 3 python × 3 observability profiles` lint/typecheck/test matrix, a generation-only file-presence matrix, and a `fastapi_db` smoke job.

After adding files to the template, `git add` them — untracked files are easy to lose in review and the diff.

## Generated project: commands & architecture

Commands (from the generated `Makefile`, run **inside** a generated project):

- `make run` — `python -m app.main`; uvicorn app factory on `0.0.0.0:8000` (`/docs`, `/redoc`)
- `make lint` (ruff format + `check --fix`) · `make lint-no-format` · `make typecheck` (`ty check`) · `make test` (pytest) · `make test-coverage` (`--cov-fail-under=90`) · `make check` (lint + typecheck + coverage)
- db types: `make up-dependencies` (docker-compose Postgres) · `make migrate` · `make migration MSG="…"` · `make upgrade` · `make downgrade`
- single test: `uv run pytest tests/api/test_examples.py::test_name -v`

Layered FastAPI app under `app/`:

- **Entry / wiring** — `main.py::create_app()` is the app factory. `api/v1/router.py` aggregates the `examples` (db) and `agents` (agent) routers; `api/health_checks` is always present. Exception handlers are registered **last**, after routers and middleware.
- **Config** — `core/config.py`: a frozen pydantic-settings `Settings`, exposed via `@lru_cache get_settings()`, loaded from `.env`.
- **Dependency Injection via FastAPI `Depends` throughout** — services receive collaborators in `__init__` (`Annotated[AsyncSession, Depends(get_session)]`); routes inject services with `Annotated[ExampleService, Depends()]`. Convention: public methods at the top of a class, private `_helpers` at the bottom.
- **`services/`** business logic; **`infrastructure/db`** (async SQLAlchemy 2.0, Alembic, fastapi-pagination) and **`infrastructure/llms`** (OpenAI + Bedrock model registry).
- **`agents/`** (pydantic-ai) — `build_examples_agent(model)` constructs the `Agent`, `get_examples_agent` is its FastAPI dependency, tools are registered with `@agent.tool`.
- **`core/observability/`** (optional) — wired by `observability.setup(app, settings)`; OTEL tracing + Prometheus metrics, with decorators `@track_inflight`, `@increment_after`, `@increment_on_error`, `@track_latency`. Structured JSON logging lives in `core/logging`.
- db migrations can auto-run on startup via `core/lifespan.py` (`MIGRATION_ON_STARTUP`).

Tests (`asyncio_mode=auto`): `tests/api` (httpx `AsyncClient` + `ASGITransport`), `tests/unit`, `tests/mocks` (agents). `tests/conftest.py` provides `app` / `client` / `session` fixtures; db tests spin up a `PostgresContainer`; agent tests set `ALLOW_MODEL_REQUESTS = False`. Override DI in tests with the helpers in `tests/dependencies.py` (`override_dependency`, `temporary_override(s)`).

## Code conventions (from `instructions.txt`; enforced by ruff/ty in generated projects)

- Modern typing only: `list[str]`, `str | None` — never `typing.List/Optional/Union`. Annotate **all** params and returns (ruff `ANN`).
- Pydantic models for any data object; no schemaless dicts. Configuration via pydantic-settings + `.env`.
- Ruff: line length 120, **single quotes**, broad rule set incl. `S` (bandit), `C90` complexity ≤ 15. Type-check with `ty`.
- Add/remove dependencies with `uv` only; drop a dependency when you remove the feature that used it.
- Self-documenting names; comment only non-obvious logic. Avoid "Final"-style iteration names.
