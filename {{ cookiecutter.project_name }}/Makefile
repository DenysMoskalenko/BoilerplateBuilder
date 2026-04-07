lint:
	uv run ruff format
	uv run ruff check --fix

lint-no-format:
	uv run ruff check

typecheck:
	uv run ty check

test:
	uv run pytest

test-coverage:
	uv run pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90

check: lint typecheck test-coverage
	@echo "✓ All checks passed"

run:
	uv run python -m app.main
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}

up-dependencies:
	docker compose up

migration:
	uv run alembic revision --autogenerate -m "$(MSG)"

migrate:
	uv run alembic upgrade head

upgrade:
	uv run alembic upgrade +1

downgrade:
	uv run alembic downgrade -1
{%- endif %}
