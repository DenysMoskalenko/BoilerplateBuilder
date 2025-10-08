# Repository Guidelines

## Project Structure & Module Organization
- This repository is a Cookiecutter template for Python projects (FastAPI or CLI).
- Key paths: `cookiecutter.json`, `hooks/`, `{{ cookiecutter.project_name }}/` (template source), `.github/`, `.pre-commit-config.yaml`, `README.md`.
- The template mirrors generated projects: `app/`, `tests/`, `migrations/` (DB types), `Dockerfile`, `docker-compose.yaml` (DB types), `Makefile`, `pyproject.toml`.

## Build, Test, and Development Commands
- Generate a project: `cookiecutter .` or `cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder`.
- After generation (inside the new project):
  - `uv sync` – install dependencies
  - `make run` – start API/CLI
  - `make lint` – format + lint via Ruff
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
- For template changes, generate at least two project types and run the full lint/test suite on each.

## Commit & Pull Request Guidelines
- Use Conventional Commits where possible: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:` (matches repo history).
- PRs should include: scope (template vs. hooks), affected project types (`fastapi_db`, `fastapi_slim`, `cli_db`, `cli_slim`), commands used to validate (e.g., `cookiecutter . --no-input project_type=fastapi_db`), and test results. Link related issues; add screenshots for docs/API changes when helpful.

## Agent-Specific Notes
- Do not render the template; edit sources under `{{ cookiecutter.project_name }}` and `hooks/` using placeholders.
- Keep `hooks/post_gen_project.py` idempotent and cross-platform; use Python 3.11+ features and avoid breaking non-target project types.
- Limit changes to the task; run `pre-commit run -a` before submitting.
