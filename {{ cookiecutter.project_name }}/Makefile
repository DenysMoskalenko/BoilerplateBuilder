lint:
	ruff format
	ruff check --fix

lint-no-format:
	ruff check

typecheck:
	ty check

test:
	pytest

test-coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90

check: lint typecheck test-coverage
	@echo "✓ All checks passed"

run:
	python -m app.main

{%- if cookiecutter.project_type in ["fastapi_db", "cli_db"] %}

up-dependencies:
	docker compose up

migration:
	alembic revision --autogenerate -m "$(MSG)"

migrate:
	alembic upgrade head

upgrade:
	alembic upgrade +1

downgrade:
	alembic downgrade -1
{%- endif %}
