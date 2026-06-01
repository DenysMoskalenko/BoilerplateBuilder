# Repository Guidelines

## Project Structure & Module Organization
- This repository is a Cookiecutter template for production-ready FastAPI projects (types: `fastapi_db_agent`, `fastapi_db`, `fastapi_agent`, `fastapi_slim`).
- Key paths: `cookiecutter.json`, `hooks/`, `{{ cookiecutter.project_name }}/` (template source), `.github/`, `.pre-commit-config.yaml`, `README.md`.
- The template mirrors generated projects: `app/`, `tests/`, `migrations/` (DB types), `Dockerfile`, `docker-compose.yaml` (DB types), `Makefile`, `pyproject.toml`.
- Generated `app/` is **package-by-feature**: business logic lives in vertical slices under `app/modules/<feature>/` (`routes.py` + `schemas.py` + `service.py`, growing a facade subpackage only when a concern needs 2+ files), while cross-cutting technical code stays in `app/core/` and `app/infrastructure/` (all SQLAlchemy models centralised in `app/infrastructure/db/models/`). Routers are aggregated in `app/router.py::create_router()`. Shipped modules: `health_checks` (all types), `examples` (db types), `examples_agent` (agent types); see `app/modules/README.md`. When you move or rename module files, update the per-type `paths_to_remove` lists in `hooks/post_gen_project.py`.

## Build, Test, and Development Commands
- Generate a project: `cookiecutter .` or `cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder`.
- After generation (inside the new project):
  - `uv sync` – install dependencies
  - `make run` – start the API
  - `make lint` – format + lint via Ruff
  - `make typecheck` – static type check via ty
  - `make test` / `make test-coverage` – run tests
- DB projects: `make up-dependencies`, `make migrate`, `make migration MSG="add feature"`.

## Coding Style & Naming Conventions
- Python 3.11+ with modern typing (`list[str]`, `str | None`). Prefer Pydantic models for data.
- Lint/format with Ruff (`uv run ruff format` and `uv run ruff check --fix`).
- Naming: modules/files `snake_case`; classes `PascalCase`; functions/vars `snake_case`; tests start with `test_`.
- Preserve Jinja placeholders exactly (e.g., `{{ cookiecutter.project_name }}`) when editing template files and paths.

## Testing Guidelines
- Framework: `pytest`. Layout: `tests/unit/` (unit), `tests/api/` (FastAPI), DB tests use testcontainers.
- Run locally: `make test` or `pytest -v`; use `make test-coverage` to review coverage.
- For template changes, validate with `python -m scripts.template_smoke_test` (generates each type, then runs `uv sync` + `make lint`/`typecheck`/`test` inside each); requires `cookiecutter`, `uv`, `make`, and Docker for DB types. At minimum cover the affected project types.
- When working on observability/local telemetry features, template verification must cover every `project_type` combined with the four `use_otel_observability`/`generate_local_otel_stack` answer pairs (yes/yes, yes/no, no/yes which must fail early, no/no) to ensure both positive and negative paths stay healthy.

## Commit & Pull Request Guidelines
- Use Conventional Commits where possible: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:` (matches repo history).
- PRs should include: scope (template vs. hooks), affected project types (`fastapi_db_agent`, `fastapi_db`, `fastapi_agent`, `fastapi_slim`), commands used to validate (e.g., `cookiecutter . --no-input project_type=fastapi_db`), and test results. Link related issues; add screenshots for docs/API changes when helpful.

## Agent-Specific Notes
- Do not render the template; edit sources under `{{ cookiecutter.project_name }}` and `hooks/` using placeholders.
- Keep `hooks/post_gen_project.py` idempotent and cross-platform; use Python 3.11+ features and avoid breaking non-target project types.
- Limit changes to the task; run `pre-commit run -a` before submitting.
- All newly created files MUST be added to git to avoid losing them during review.
