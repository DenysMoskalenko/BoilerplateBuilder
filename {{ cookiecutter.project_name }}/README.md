{%- if cookiecutter.project_type == "fastapi_db" %}
# {{ cookiecutter.project_name }}

### Locally:

1. (Optional) Install required 3.12 python `uv python install 3.12` if not installed
2. Create virtual environment: `uv venv --python 3.12`
3. Activate environment `source .venv/bin/activate`
4. Install project dependencies: `uv sync`
5. Edit `.env` file with your real values if needed (check `dist.env` for reference)
6. Run app: `make run`

### Before PR:

1. Run linter using `make lint`
2. Run tests using `make test` (Up dependencies if needed)

### Creation of pre-commit hook

After you installed all dependencies(including dev dependencies):

1. Create `.pre-commit-config.yaml` file with your settings.
   We usually use [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
2. run `pre-commit install` to activate tour pre-commit hook

### Git setup

Before making any commits—ensure you are using correct work profile.

1. Check you name/email by `git config user.name` and `git config user.email`
2. Change name/email by `git config user.name "Your Fullname"`/`git config user.email "YourWorkEmail"`
{%- elif cookiecutter.project_type == "fastapi_slim" %}
# {{ cookiecutter.project_name }}

### Locally:

1. (Optional) Install required 3.12 python `uv python install 3.12` if not installed
2. Create virtual environment: `uv venv --python 3.12`
3. Activate environment `source .venv/bin/activate`
4. Install project dependencies: `uv sync`
5. Edit `.env` file with your real values if needed (check `dist.env` for reference)
6. Run app: `make run`

### Before PR:

1. Run linter using `make lint`
2. Run tests using `make test`

### Creation of pre-commit hook

After you installed all dependencies(including dev dependencies):

1. Create `.pre-commit-config.yaml` file with your settings.
   We usually use [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
2. run `pre-commit install` to activate tour pre-commit hook

### Git setup

Before making any commits—ensure you are using correct work profile.

1. Check you name/email by `git config user.name` and `git config user.email`
2. Change name/email by `git config user.name "Your Fullname"`/`git config user.email "YourWorkEmail"`
{%- else %}
# {{ cookiecutter.project_name }}

### Locally:

1. (Optional) Install required 3.12 python `uv python install 3.12` if not installed
2. Create virtual environment: `uv venv --python 3.12`
3. Activate environment `source .venv/bin/activate`
4. Install project dependencies: `uv sync`
5. Edit `.env` file with your real values if needed (check `dist.env` for reference)
6. Run app: `make run`

### Before PR:

1. Run linter using `make lint`
2. Run tests using `make test`

### Creation of pre-commit hook

After you installed all dependencies(including dev dependencies):

1. Create `.pre-commit-config.yaml` file with your settings.
   We usually use [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
2. run `pre-commit install` to activate tour pre-commit hook

### Git setup

Before making any commits—ensure you are using correct work profile.

1. Check you name/email by `git config user.name` and `git config user.email`
2. Change name/email by `git config user.name "Your Fullname"`/`git config user.email "YourWorkEmail"`
{%- endif %}
