#!/usr/bin/env python
"""Post-generation hook for cookiecutter."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def validate_observability_config():
    """Validate that observability configuration is consistent."""
    use_otel_observability = "{{ cookiecutter.use_otel_observability }}"
    generate_local_otel_stack = "{{ cookiecutter.generate_local_otel_stack }}"

    if generate_local_otel_stack == "yes" and use_otel_observability != "yes":
        print("\n❌ ERROR: Invalid configuration!")
        print("   'generate_local_otel_stack' cannot be 'yes' when 'use_otel_observability' is 'no'.")
        print("   The local telemetry stack requires observability to be enabled.")
        print("   Please regenerate the project with 'use_otel_observability=yes' or 'generate_local_otel_stack=no'.\n")

        # Clean up the generated project directory
        project_dir = Path.cwd()  # Current directory (the generated project)
        parent_dir = project_dir.parent  # Where cookiecutter was originally run
        project_name = project_dir.name

        print(f"🧹 Cleaning up generated project directory '{project_name}'...")
        try:
            # Change to parent directory before removing
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

    # When this hook runs, we are already inside the generated project directory
    # We need to move all contents from here to the parent directory
    project_dir = Path.cwd()  # Current directory (inside the generated project)
    parent_dir = project_dir.parent  # Where cookiecutter was originally run
    project_name = "{{ cookiecutter.project_name }}"

    print(f"📁 Extracting content from {project_name}/ to parent directory...")

    # Move all files and directories from project_dir to parent_dir
    for item in project_dir.iterdir():
        dest_path = parent_dir / item.name

        # If destination exists, we need to handle the conflict
        if dest_path.exists():
            if dest_path.is_dir() and item.is_dir():
                # Merge directories by moving contents
                for sub_item in item.iterdir():
                    sub_dest = dest_path / sub_item.name
                    if sub_dest.exists():
                        if sub_dest.is_dir():
                            shutil.rmtree(sub_dest)
                        else:
                            sub_dest.unlink()
                    shutil.move(str(sub_item), str(sub_dest))
                # Remove the now-empty source directory
                item.rmdir()
            else:
                # Replace file/directory
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
                shutil.move(str(item), str(dest_path))
        else:
            # No conflict, just move
            shutil.move(str(item), str(dest_path))

    # Change working directory to parent directory for subsequent operations
    os.chdir(parent_dir)

    # Remove the now-empty project directory
    if project_dir.exists() and not any(project_dir.iterdir()):
        project_dir.rmdir()
        print(f"✓ Content extracted to current directory, removed empty {project_name}/ directory")



def remove_empty_files():
    """Remove files that were conditionally empty."""
    project_root = Path.cwd()
    project_type = "{{ cookiecutter.project_type }}"
    use_otel_observability = "{{ cookiecutter.use_otel_observability }}"
    generate_local_otel_stack = "{{ cookiecutter.generate_local_otel_stack }}"

    # Remove observability directories if observability is disabled
    if use_otel_observability != "yes":
        observability_paths = [
            project_root / "app" / "observability",
            project_root / "tests" / "unit" / "observability",
        ]
        for path in observability_paths:
            if path.exists():
                try:
                    shutil.rmtree(path)
                    print(f"Removed {path.relative_to(project_root)} (observability is disabled)")
                except Exception as e:
                    print(f"Warning: Could not remove {path}: {e}")

        # Remove observability-related files
        observability_files = [
            project_root / "tests" / "unit" / "test_config_validators.py",
        ]
        for file_path in observability_files:
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"Removed {file_path.relative_to(project_root)} (observability is disabled)")
                except Exception as e:
                    print(f"Warning: Could not remove {file_path}: {e}")

    # Remove local telemetry stack if not using it
    if generate_local_otel_stack != "yes":
        local_telemetry_path = project_root / "local_telemetry"
        if local_telemetry_path.exists():
            try:
                shutil.rmtree(local_telemetry_path)
                print(f"Removed {local_telemetry_path.relative_to(project_root)} (local telemetry stack is disabled)")
            except Exception as e:
                print(f"Warning: Could not remove {local_telemetry_path}: {e}")

    # Remove docker-compose.yaml if not a database project and no local telemetry stack
    if project_type not in ["fastapi_db", "cli_db"] and generate_local_otel_stack != "yes":
        docker_compose_path = project_root / "docker-compose.yaml"
        if docker_compose_path.exists():
            docker_compose_path.unlink()
            print("Removed docker-compose.yaml (not needed for this project type)")

    # For CLI projects, remove FastAPI-specific files and directories
    if project_type == "cli_slim":
        cli_cleanup_paths = [
            "app/api",
            "app/models",
            "migrations",
            "alembic.ini",
            "app/core/database.py",
            "app/core/exception_handlers.py",
            "app/core/lifespan.py",
            "tests/api",
            "tests/dependencies.py",
            "tests/factories.py",
        ]

        for path_str in cli_cleanup_paths:
            path = project_root / path_str
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed directory: {path_str}")
                else:
                    path.unlink()
                    print(f"Removed file: {path_str}")

    # For FastAPI DB, remove unit tests folder (only CLI should have it)
    # but keep tests/unit if observability is enabled (contains observability tests)
    if project_type == "fastapi_db" and use_otel_observability != "yes":
        db_cleanup_paths = [
            "tests/unit",  # Remove unit tests folder for fastapi_db (unless observability enabled)
        ]

        for path_str in db_cleanup_paths:
            path = project_root / path_str
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed directory: {path_str}")
                else:
                    path.unlink()
                    print(f"Removed file: {path_str}")
    elif project_type == "fastapi_db" and use_otel_observability == "yes":
        # For fastapi_db with observability, only remove test_dummy.py
        dummy_test_path = project_root / "tests/unit/test_dummy.py"
        if dummy_test_path.exists():
            dummy_test_path.unlink()
            print("Removed tests/unit/test_dummy.py (not needed with observability tests)")

    # For FastAPI Slim, remove examples API but keep health_checks
    # Keep tests/unit if observability is enabled
    if project_type == "fastapi_slim":
        slim_cleanup_paths = [
            "app/api/examples",
            "app/models",
            "migrations",
            "alembic.ini",
            "app/core/database.py",
            "app/core/exception_handlers.py",
            "tests/api/test_example.py",
            "tests/factories.py",
        ]
        if use_otel_observability != "yes":
            slim_cleanup_paths.append("tests/unit")  # Only remove if no observability

        for path_str in slim_cleanup_paths:
            path = project_root / path_str
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed directory: {path_str}")
                else:
                    path.unlink()
                    print(f"Removed file: {path_str}")

        # For fastapi_slim with observability, remove test_dummy.py but keep observability tests
        if use_otel_observability == "yes":
            dummy_test_path = project_root / "tests/unit/test_dummy.py"
            if dummy_test_path.exists():
                dummy_test_path.unlink()
                print("Removed tests/unit/test_dummy.py (not needed with observability tests)")

    # For CLI DB, remove FastAPI-specific files but keep database files
    if project_type == "cli_db":
        cli_db_cleanup_paths = [
            "app/api",
            "app/core/exception_handlers.py",
            "app/core/lifespan.py",
            "tests/api",
            "tests/dependencies.py",
        ]

        for path_str in cli_db_cleanup_paths:
            path = project_root / path_str
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    print(f"Removed directory: {path_str}")
                else:
                    path.unlink()
                    print(f"Removed file: {path_str}")

    # Remove .pre-commit-config.yaml if it's empty (when use_pre_commit == "no")
    pre_commit_path = project_root / ".pre-commit-config.yaml"
    if pre_commit_path.exists() and pre_commit_path.stat().st_size == 0:
        pre_commit_path.unlink()
        print("Removed empty .pre-commit-config.yaml")

    # Remove .github/workflows/ci.yml if it's empty
    ci_workflow_path = project_root / ".github/workflows/ci.yml"
    if ci_workflow_path.exists() and ci_workflow_path.stat().st_size == 0:
        ci_workflow_path.unlink()
        print("Removed empty .github/workflows/ci.yml")

    # Remove empty directories
    for dir_path in [".github/workflows", ".github"]:
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

        # Create initial commit
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from cookiecutter template"],
            check=True,
            capture_output=True
        )
        print("✓ Created initial commit")
    except subprocess.CalledProcessError:
        print("⚠ Failed to initialize git repository")
    except FileNotFoundError:
        print("⚠ Git not found, skipping repository initialization")


def install_dependencies():
    """Install project dependencies using uv."""
    try:
        # Check if uv is installed
        subprocess.run(["uv", "--version"], check=True, capture_output=True)

        print("Installing dependencies...")
        # First create the lock file
        subprocess.run(["uv", "lock"], check=True)
        print("✓ Created uv.lock file")

        # Then sync dependencies
        subprocess.run(["uv", "sync"], check=True)
        print("✓ Dependencies installed successfully!")

        # Install pre-commit hooks if enabled and git is initialized
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


def remove_leading_empty_lines():
    """Remove leading empty lines from all files."""
    project_root = Path.cwd()

    # File extensions to process
    extensions_to_process = {'.py', '.yml', '.yaml', '.toml', '.md', '.txt', '.cfg', '.ini', '.env'}

    files_processed = 0
    for file_path in project_root.rglob('*'):
        # Skip directories, hidden files, and files in .venv or other ignored directories
        if (file_path.is_dir() or
            file_path.name.startswith('.') or
            '.venv' in str(file_path) or
            '__pycache__' in str(file_path)):
            continue

        # Process files with relevant extensions or no extension
        if file_path.suffix.lower() in extensions_to_process or not file_path.suffix:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Find first non-empty line
                first_content_line = 0
                for i, line in enumerate(lines):
                    if line.strip():  # Non-empty line found
                        first_content_line = i
                        break
                else:
                    # File is completely empty or only whitespace
                    continue

                # If there are empty lines before content, remove them
                if first_content_line > 0:
                    new_lines = lines[first_content_line:]
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                    files_processed += 1
                    print(f"Removed {first_content_line} leading empty line(s) from: {file_path.relative_to(project_root)}")

            except (UnicodeDecodeError, PermissionError):
                # Skip binary files or files we can't read
                continue

    if files_processed > 0:
        print(f"✓ Processed {files_processed} files to remove leading empty lines")


def run_linter_and_formatter():
    """Run linter and formatter on the generated project."""
    try:
        print("Running linter and formatter...")
        # Run ruff format to format the code
        subprocess.run(["uv", "run", "ruff", "format", "."], check=True, capture_output=True)
        print("✓ Code formatted successfully")

        # Run ruff check to lint the code
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
    project_type = "{{ cookiecutter.project_type }}"
    extract_to_current = "{{ cookiecutter.extract_to_current_dir }}"

    print("\n" + "="*60)
    print(f"🎉 Project {project_name} created successfully!")
    print("="*60)

    print(f"\n📁 Project type: {project_type}")
    if extract_to_current == "Extract Here":
        print("   Project files extracted to current directory")
    else:
        print(f"   cd {project_name}")

    print("\n🚀 Next steps:")
    print("   1. Review and update the .env file with your configuration")

    if project_type in ["fastapi_db", "cli_db"]:
        print("   2. Set up your database:")
        print("      - Run: make up-dependencies  # Start PostgreSQL container")
        print("      - Or ensure PostgreSQL is running locally and update DATABASE_URL in .env")
        print("      - Run: uv run alembic upgrade head  # Apply migrations")

    print("\n📖 Available commands:")
    print("   - make lint          # Run linter and formatter")
    print("   - make lint-no-format  # Run linter only")
    print("   - make test          # Run tests")
    print("   - make test-coverage # Run tests with coverage report")
    print("   - make run           # Run the application")

    if project_type in ["fastapi_db", "cli_db"]:
        print("\n🗄️  Database commands:")
        print("   - make up-dependencies   # Start PostgreSQL container")
        print("   - make migration MSG='description'  # Create new migration")
        print("   - make migrate       # Apply all migrations")
        print("   - make upgrade       # Apply next migration")
        print("   - make downgrade     # Rollback last migration")

    if project_type in ["fastapi_db", "fastapi_slim"]:
        print("\n🌐 Once running, visit:")
        print("   - http://localhost:8000       # API root")
        print("   - http://localhost:8000/docs  # Interactive API documentation")
        print("   - http://localhost:8000/redoc # Alternative API documentation")

    print("\n🐳 Docker available:")
    print(f"   - docker build -t {project_name.lower()} .")
    if project_type in ["fastapi_db", "fastapi_slim"]:
        print(f"   - docker run -p 8000:8000 {project_name.lower()}")
    else:
        print(f"   - docker run {project_name.lower()}")

    print("\n💡 Tips:")
    print("   - Dependencies are managed with uv (https://github.com/astral-sh/uv)")
    print("   - Code is formatted with ruff")
    if project_type in ["fastapi_db", "cli_db"]:
        print("   - Database migrations use Alembic")

    print("\n" + "="*60)


def main():
    """Main post-generation script."""
    print("\n🔧 Running post-generation tasks...")

    # Validate observability configuration (must be first)
    validate_observability_config()

    # Extract to current directory if requested
    extract_to_current_directory()

    # Clean up conditional empty files
    remove_empty_files()

    # Remove leading empty lines from all files
    remove_leading_empty_lines()

    # Create .env file
    create_env_file()

    # Install dependencies
    install_dependencies()

    # Run linter and formatter
    run_linter_and_formatter()

    # Initialize git repository (LAST step before success message to add everything to git)
    initialize_git()

    # Display success message
    display_success_message()


if __name__ == "__main__":
    main()
