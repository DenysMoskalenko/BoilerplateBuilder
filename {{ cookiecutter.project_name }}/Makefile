lint:
	ruff format
	ruff check --fix

lint-no-format:
	ruff check

test:
	pytest

test-coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90

{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
run:
	uvicorn app.main:app --reload --port=8000
{%- else %}
run:
	python -m app.main
{%- endif %}

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
