#!/usr/bin/env python
"""Post-generation hook for cookiecutter."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_TYPE = "{{ cookiecutter.project_type }}"
USE_OTEL = "{{ cookiecutter.use_otel_observability }}"
USE_PRE_COMMIT = "{{ cookiecutter.use_pre_commit }}"
GENERATE_LOCAL_STACK = "{{ cookiecutter.generate_local_otel_stack }}"

IS_DB = PROJECT_TYPE in ("fastapi_db", "fastapi_db_agent")
IS_AGENT = PROJECT_TYPE in ("fastapi_agent", "fastapi_db_agent")


def validate_observability_config():
    """Validate that observability configuration is consistent."""
    if GENERATE_LOCAL_STACK == "yes" and USE_OTEL != "yes":
        print("\n❌ ERROR: Invalid configuration!")
        print("   'generate_local_otel_stack' cannot be 'yes' when 'use_otel_observability' is 'no'.")
        print("   The local telemetry stack requires observability to be enabled.")
        print("   Please regenerate the project with 'use_otel_observability=yes' or 'generate_local_otel_stack=no'.\n")

        project_dir = Path.cwd()
        parent_dir = project_dir.parent
        project_name = project_dir.name

        print(f"🧹 Cleaning up generated project directory '{project_name}'...")
        try:
            os.chdir(parent_dir)
            if project_dir.exists():
                shutil.rmtree(project_dir)
                print(f"✓ Removed '{project_name}' directory")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove generated directory: {e}")
            print(f"   Please manually remove '{project_dir}' if needed.")

        sys.exit(1)


def extract_to_current_directory():
    """Extract template content to current directory if requested."""
    extract_to_current = "{{ cookiecutter.extract_to_current_dir }}"
    if extract_to_current != "Extract Here":
        return

    project_dir = Path.cwd()
    parent_dir = project_dir.parent
    project_name = "{{ cookiecutter.project_name }}"

    print(f"📁 Extracting content from {project_name}/ to parent directory...")

    for item in project_dir.iterdir():
        dest_path = parent_dir / item.name

        if dest_path.exists():
            if dest_path.is_dir() and item.is_dir():
                for sub_item in item.iterdir():
                    sub_dest = dest_path / sub_item.name
                    if sub_dest.exists():
                        if sub_dest.is_dir():
                            shutil.rmtree(sub_dest)
                        else:
                            sub_dest.unlink()
                    shutil.move(str(sub_item), str(sub_dest))
                item.rmdir()
            else:
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
                shutil.move(str(item), str(dest_path))
        else:
            shutil.move(str(item), str(dest_path))

    os.chdir(parent_dir)

    if project_dir.exists() and not any(project_dir.iterdir()):
        project_dir.rmdir()
        print(f"✓ Content extracted to current directory, removed empty {project_name}/ directory")


def _remove_path(project_root: Path, path_str: str) -> None:
    """Remove a file or directory relative to project_root."""
    path = project_root / path_str
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
        print(f"Removed directory: {path_str}")
    else:
        path.unlink()
        print(f"Removed file: {path_str}")


def remove_empty_files():
    """Remove files that are not needed for the selected project type."""
    project_root = Path.cwd()

    # --- Observability cleanup ---
    if USE_OTEL != "yes":
        for p in ("app/observability", "tests/unit/observability", "tests/unit/test_config_validators.py"):
            _remove_path(project_root, p)

    if GENERATE_LOCAL_STACK != "yes":
        _remove_path(project_root, "local_telemetry")

    # --- Type-specific cleanup ---
    if PROJECT_TYPE == "fastapi_slim":
        paths_to_remove = [
            "app/infrastructure",
            "app/services",
            "app/agents",
            "app/api/v1",
            "app/api/health_checks/checks.py",
            "app/core/enums.py",
            "app/core/schemas.py",
            "app/core/exceptions.py",
            "app/core/exception_handlers.py",
            "app/core/lifespan.py",
            "migrations",
            "alembic.ini",
            "tests/api/test_examples.py",
            "tests/api/test_agents.py",
            "tests/factories.py",
            "tests/mocks",
        ]
        for p in paths_to_remove:
            _remove_path(project_root, p)

    elif PROJECT_TYPE == "fastapi_db":
        paths_to_remove = [
            "app/infrastructure/llms",
            "app/agents",
            "app/api/v1/agents",
            "app/services/example_agent_service.py",
            "app/core/enums.py",
            "tests/api/test_agents.py",
            "tests/mocks",
        ]
        for p in paths_to_remove:
            _remove_path(project_root, p)

    elif PROJECT_TYPE == "fastapi_agent":
        paths_to_remove = [
            "app/infrastructure/db",
            "app/api/v1/examples",
            "app/services/example_service.py",
            "app/core/schemas.py",
            "app/core/exceptions.py",
            "app/core/lifespan.py",
            "migrations",
            "alembic.ini",
            "tests/api/test_examples.py",
            "tests/factories.py",
        ]
        for p in paths_to_remove:
            _remove_path(project_root, p)

    # fastapi_db_agent keeps everything

    # --- docker-compose cleanup ---
    if not IS_DB and GENERATE_LOCAL_STACK != "yes":
        _remove_path(project_root, "docker-compose.yaml")

    # --- Unit tests cleanup (otel-dependent) ---
    if USE_OTEL != "yes":
        _remove_path(project_root, "tests/unit")
    else:
        _remove_path(project_root, "tests/unit/test_dummy.py")

    # --- Optional config files ---
    if USE_PRE_COMMIT != "yes":
        _remove_path(project_root, ".pre-commit-config.yaml")

    ci_workflow_path = project_root / ".github/workflows/ci.yml"
    if ci_workflow_path.exists() and ci_workflow_path.stat().st_size == 0:
        ci_workflow_path.unlink()
        print("Removed empty .github/workflows/ci.yml")

    for dir_path in (".github/workflows", ".github"):
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir() and not any(full_path.iterdir()):
            full_path.rmdir()
            print(f"Removed empty directory: {dir_path}")


def initialize_git():
    """Initialize git repository."""
    initialize_git_option = "{{ cookiecutter.initialize_git }}"
    if initialize_git_option.lower() != "yes":
        return

    try:
        subprocess.run(["git", "init"], check=True, capture_output=True)
        print("✓ Initialized git repository")

        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from cookiecutter template"],
            check=True,
            capture_output=True,
        )
        print("✓ Created initial commit")
    except subprocess.CalledProcessError:
        print("⚠ Failed to initialize git repository")
    except FileNotFoundError:
        print("⚠ Git not found, skipping repository initialization")


def install_dependencies():
    """Install project dependencies using uv."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)

        print("Installing dependencies...")
        subprocess.run(["uv", "lock"], check=True)
        print("✓ Created uv.lock file")

        subprocess.run(["uv", "sync"], check=True)
        print("✓ Dependencies installed successfully!")

        if Path(".pre-commit-config.yaml").exists() and Path(".git").exists():
            try:
                subprocess.run(["uv", "run", "pre-commit", "install"], check=True, capture_output=True)
                print("✓ Pre-commit hooks installed")
            except subprocess.CalledProcessError:
                print("⚠ Failed to install pre-commit hooks")
        elif Path(".pre-commit-config.yaml").exists() and not Path(".git").exists():
            print("⚠ Skipping pre-commit hooks installation (git not initialized)")
    except FileNotFoundError:
        print("⚠ uv not found. Please install uv and run 'uv lock && uv sync' to install dependencies")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Failed to install dependencies: {e}")


def create_env_file():
    """Create .env file from dist.env."""
    if Path("dist.env").exists():
        shutil.copy("dist.env", ".env")
        print("✓ Created .env file from dist.env")


def remove_empty_python_files_content():
    """Remove content from Python files that only contain whitespace (Jinja rendering artifacts)."""
    project_root = Path.cwd()
    count = 0
    for file_path in project_root.rglob("*.py"):
        if ".venv" in str(file_path) or "__pycache__" in str(file_path):
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
            if content.strip() == "":
                file_path.write_text("", encoding="utf-8")
                count += 1
        except (UnicodeDecodeError, PermissionError):
            continue
    if count > 0:
        print(f"✓ Cleaned {count} empty Python files")


def remove_leading_empty_lines():
    """Remove leading empty lines from all files."""
    project_root = Path.cwd()
    extensions_to_process = {".py", ".yml", ".yaml", ".toml", ".md", ".txt", ".cfg", ".ini", ".env"}

    files_processed = 0
    for file_path in project_root.rglob("*"):
        if (
            file_path.is_dir()
            or file_path.name.startswith(".")
            or ".venv" in str(file_path)
            or "__pycache__" in str(file_path)
        ):
            continue

        if file_path.suffix.lower() in extensions_to_process or not file_path.suffix:
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                first_content_line = 0
                for i, line in enumerate(lines):
                    if line.strip():
                        first_content_line = i
                        break
                else:
                    continue

                if first_content_line > 0:
                    new_lines = lines[first_content_line:]
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    files_processed += 1
                    print(f"Removed {first_content_line} leading empty line(s) from: {file_path.relative_to(project_root)}")
            except (UnicodeDecodeError, PermissionError):
                continue

    if files_processed > 0:
        print(f"✓ Processed {files_processed} files to remove leading empty lines")


def run_linter_and_formatter():
    """Run linter and formatter on the generated project."""
    try:
        print("Running linter and formatter...")
        subprocess.run(["uv", "run", "ruff", "format", "."], check=True, capture_output=True)
        print("✓ Code formatted successfully")

        result = subprocess.run(["uv", "run", "ruff", "check", ".", "--fix"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Linting passed successfully")
        else:
            print("⚠ Linting found some issues:")
            print(result.stdout)
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"⚠ Failed to run linter/formatter: {e}")
    except FileNotFoundError:
        print("⚠ uv or ruff not found, skipping linting/formatting")


def display_success_message():
    """Display success message with next steps."""
    project_name = "{{ cookiecutter.project_name }}"
    extract_to_current = "{{ cookiecutter.extract_to_current_dir }}"

    print("\n" + "=" * 60)
    print(f"🎉 Project {project_name} created successfully!")
    print("=" * 60)

    print(f"\n📁 Project type: {PROJECT_TYPE}")
    if extract_to_current == "Extract Here":
        print("   Project files extracted to current directory")
    else:
        print(f"   cd {project_name}")

    print("\n🚀 Next steps:")
    print("   1. Review and update the .env file with your configuration")

    if IS_DB:
        print("   2. Set up your database:")
        print("      - Run: make up-dependencies  # Start PostgreSQL container")
        print("      - Or ensure PostgreSQL is running locally and update DATABASE_URL in .env")
        print("      - Run: uv run alembic upgrade head  # Apply migrations")

    if IS_AGENT:
        print(f"   {'3' if IS_DB else '2'}. Configure AI providers:")
        print("      - Set OPENAI_API_KEY in .env for OpenAI models")
        print("      - Set AWS credentials in .env for Bedrock models")

    print("\n📖 Available commands:")
    print("   - make lint          # Run linter and formatter")
    print("   - make lint-no-format  # Run linter only")
    print("   - make test          # Run tests")
    print("   - make test-coverage # Run tests with coverage report")
    print("   - make run           # Run the application")

    if IS_DB:
        print("\n🗄️  Database commands:")
        print("   - make up-dependencies   # Start PostgreSQL container")
        print("   - make migration MSG='description'  # Create new migration")
        print("   - make migrate       # Apply all migrations")
        print("   - make upgrade       # Apply next migration")
        print("   - make downgrade     # Rollback last migration")

    print("\n🌐 Once running, visit:")
    print("   - http://localhost:8000       # API root")
    print("   - http://localhost:8000/docs  # Interactive API documentation")
    print("   - http://localhost:8000/redoc # Alternative API documentation")

    print("\n🐳 Docker available:")
    print(f"   - docker build -t {project_name.lower()} .")
    print(f"   - docker run -p 8000:8000 {project_name.lower()}")

    print("\n💡 Tips:")
    print("   - Dependencies are managed with uv (https://github.com/astral-sh/uv)")
    print("   - Code is formatted with ruff")
    if IS_DB:
        print("   - Database migrations use Alembic")
    if IS_AGENT:
        print("   - AI agents powered by pydantic-ai")

    print("\n" + "=" * 60)


def main():
    """Main post-generation script."""
    print("\n🔧 Running post-generation tasks...")

    validate_observability_config()
    extract_to_current_directory()
    remove_empty_files()
    create_env_file()
    install_dependencies()
    run_linter_and_formatter()
    remove_empty_python_files_content()
    remove_leading_empty_lines()
    initialize_git()
    display_success_message()


if __name__ == "__main__":
    main()
