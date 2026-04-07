# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

### Locally:

1. (Optional) Install required {{ cookiecutter.python_version }} python `uv python install {{ cookiecutter.python_version }}` if not installed
2. Create virtual environment: `uv venv --python {{ cookiecutter.python_version }}`
3. Activate environment `source .venv/bin/activate`
4. Install project dependencies: `uv sync`
5. Edit `.env` file with your real values if needed (check `dist.env` for reference)
{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
6. Start dependencies: `make up-dependencies`
7. Run migrations: `make migrate`
8. Run app: `make run`
{%- else %}
6. Run app: `make run`
{%- endif %}

After start, API docs are available at:
- http://localhost:8000/docs - Interactive Swagger UI
- http://localhost:8000/redoc - ReDoc documentation

### Before PR:

1. Run linter using `make lint`
2. Run tests using `make test` (up dependencies if needed)
3. Run all checks using `make check` (lint + typecheck + coverage)

### Creation of a pre-commit hook

After you installed all dependencies (including dev dependencies):

1. Create `.pre-commit-config.yaml` file with your settings.
   We usually use [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
2. Run `prek install` to activate your pre-commit hook

### Git setup

Before making any commits -- ensure you are using correct work profile.

1. Check your name/email by `git config user.name` and `git config user.email`
2. Change name/email by `git config user.name "Your Fullname"`/`git config user.email "YourWorkEmail"`
3. Configure Git for commit signing `git config user.signingkey YOUR_KEY_ID` and `git config commit.gpgsign true`. Check
   your keys by `gpg --list-secret-keys --keyid-format=long`
4. Force Signing: always use `git commit -S` for explicit signing or let your IDE do the job
