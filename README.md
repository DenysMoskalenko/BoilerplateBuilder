# Python Project Boilerplate Builder 🏗️

A modern cookiecutter template for generating Python projects with FastAPI or CLI applications, including database
support, Docker, testing, and CI/CD setup.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- [cookiecutter](https://github.com/cookiecutter/cookiecutter)

### Installation

```bash
# Install cookiecutter
pip install cookiecutter
# or
uv add cookiecutter

# Generate a new project
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder
```

## 📋 Project Types

This template supports **4 different project types**:

### 1. **`fastapi_db`** - Full FastAPI with Database

- ✅ FastAPI web framework with async support
- ✅ PostgreSQL database with SQLAlchemy 2.0
- ✅ Alembic migrations
- ✅ Docker & docker-compose setup
- ✅ API examples and health checks
- ✅ Comprehensive testing with testcontainers
- ✅ GitHub Actions CI/CD

**Use case**: Production-ready web APIs with database persistence

### 2. **`fastapi_slim`** - Minimal FastAPI

- ✅ FastAPI web framework
- ✅ Health check endpoints
- ✅ Docker support
- ✅ Basic testing setup
- ✅ GitHub Actions CI/CD
- ❌ No database dependencies

**Use case**: Lightweight APIs, microservices, prototypes

### 3. **`cli_db`** - CLI Application with Database

- ✅ Command-line interface
- ✅ PostgreSQL database with SQLAlchemy 2.0
- ✅ Alembic migrations
- ✅ Docker & docker-compose for database
- ✅ Database testing with testcontainers
- ✅ GitHub Actions CI/CD

**Use case**: Data processing scripts, ETL tools, database utilities

### 4. **`cli_slim`** - Minimal CLI Application

- ✅ Simple command-line interface
- ✅ Docker support
- ✅ Unit testing
- ✅ GitHub Actions CI/CD
- ❌ No database dependencies

**Use case**: Utilities, scripts, simple automation tools

## 🛠️ Features

### Common Features (All Projects)

- 🐍 **Modern Python** with type hints and async support
- 📦 **uv** for fast dependency management
- 🧹 **Code Quality**: Ruff for linting and formatting
- 🧪 **Testing**: pytest with async support and coverage
- 🔧 **Pre-commit hooks** (optional)
- 🐳 **Docker** with multi-stage builds and BuildKit caching
- 🎯 **Makefile** with common commands
- ⚙️ **GitHub Actions** CI/CD (optional)
- 📝 **Git initialization** (optional)

### Database Projects Features

- 🗄️ **PostgreSQL** with async SQLAlchemy 2.0
- 🔄 **Alembic** migrations with auto-generation
- 🐳 **Docker Compose** with PostgreSQL container
- 🧪 **Database testing** with testcontainers
- 📊 **Example models** and database operations

### FastAPI Projects Features

- 🚀 **FastAPI** with automatic OpenAPI docs
- 🏥 **Health check** endpoints
- 🔧 **Exception handling** and middleware
- 🧪 **HTTP client testing** with httpx
- 📚 **Interactive API docs** at `/docs` and `/redoc`

### Cursor IDE Integration (Optional)

- 🎯 **18 Comprehensive Python Rules** for consistent code style
- 🔧 **Automatic Code Guidance** in Cursor IDE
- 📋 **Organized Categories**: Core language, tooling, architecture, workflow
- ⚡ **Modern Python 3.12+** features and best practices
- 🏗️ **Pydantic-first** approach for data modeling
- 🧪 **Testing & Linting** automation rules
- 📦 **UV & Ruff** integration standards

The Cursor rules include:
- **Core Language (1-6)**: Modern Python features, typing, self-documenting code
- **Development Tools (7-13)**: UV package manager, Ruff linting, pytest workflows
- **Architecture (14-16)**: Pydantic models, settings management, dependency injection
- **Workflow (17-18)**: Task focus, code preservation practices

## 📖 Usage

### Interactive Generation

```bash
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder
```

You'll be prompted for:

- **Extract to current dir**: Choose "Create New" (default) or "Extract Here" to extract files directly to current directory
- **Project name**: Your project name
- **Project description**: Brief description
- **Author name**: Your name
- **Author email**: Your email
- **Project type**: Choose from `fastapi_db`, `fastapi_slim`, `cli_db`, `cli_slim`
- **Python version**: 3.11 or 3.12
- **Pre-commit hooks**: Enable/disable pre-commit
- **GitHub Actions**: Enable/disable CI/CD
- **Git initialization**: Auto-initialize git repo
- **Cursor rules**: Include comprehensive Python coding rules for Cursor IDE (optional)

### Non-Interactive Generation

```bash
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder \
  --no-input \
  extract_to_current_dir="Create New" \
  project_name="MyAwesomeAPI" \
  project_type="fastapi_db" \
  author_name="John Doe" \
  author_email="john@example.com" \
  add_cursor_rules="yes"
```

### Extract to Existing Repository

If you already have a Git repository and want to add the boilerplate directly to it:

```bash
# Navigate to your existing repository
cd my-existing-repo

# Generate project and extract to current directory
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder \
  --no-input \
  extract_to_current_dir="Extract Here" \
  project_name="MyAPI" \
  project_type="fastapi_db"
```

This will:
- Generate the template in a temporary subdirectory
- Move all files to your current directory
- Remove the temporary subdirectory
- Template files will overwrite any existing files with the same name

## 🏃‍♂️ Getting Started with Generated Project

### 1. Enter your project directory

```bash
# If extracted to current directory, you're already there
# Otherwise:
cd your-project-name
```

### 2. Set up environment

```bash
# Install dependencies (done automatically during generation)
uv sync

# Edit .env with your real values if needed
```

### 3. Database projects only

```bash
# Start PostgreSQL container
make up-dependencies

# Run migrations
make migrate
```

### 4. Run your project

```bash
# FastAPI projects
make run
# Visit http://localhost:8000/docs

# CLI projects
make run
```

### 5. Development commands

```bash
make lint              # Format and lint code
make test              # Run tests
make test-coverage     # Run tests with coverage
```

### 6. Cursor IDE Rules (if enabled)

If you selected "yes" for Cursor rules, your project includes a `.cursor/rules/` directory with:

- **Automatic code guidance** when writing Python code
- **18 organized rules** covering modern Python practices
- **Consistent style enforcement** across your team
- **Built-in examples** for FastAPI, Pydantic, and SQLAlchemy patterns

**Using with Cursor IDE:**
1. Open your project in Cursor IDE
2. The rules automatically activate for any Python files
3. Cursor will suggest code following the established patterns
4. Rules cover everything from typing to testing workflows

**Rule organization:**
- `00-index.mdc` - Overview of all rules
- `01-python-core.mdc` - Core language features
- `02-python-tooling.mdc` - Development tools
- `03-python-architecture.mdc` - Data modeling & DI
- `04-python-workflow.mdc` - Development practices

## 🗄️ Database Projects

### Database Setup Options

#### Option 1: Docker (Recommended)

```bash
make up-dependencies   # Start PostgreSQL container
make migrate          # Apply migrations
```

#### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL locally
# Update DATABASE_URL in .env
make migrate          # Apply migrations
```

### Database Commands

```bash
make migration MSG="add users table"  # Create new migration
make migrate                         # Apply all migrations
make upgrade                         # Apply next migration
make downgrade                       # Rollback last migration
```

### Example Database Operations

```python
# In your CLI or API code
from app.core.database import open_db_session
from app.models.example import ExampleModel


async def create_example():
    async with open_db_session() as session:
        example = ExampleModel(name="test", birthday=None)
        session.add(example)
        # Session auto-commits on context exit
```

## 🐳 Docker

### Build and Run

```bash
# Build image
docker build -t myproject .

# Run FastAPI projects
docker run -p 8000:8000 myproject

# Run CLI projects
docker run myproject
```

### Production Deployment

The generated Dockerfile uses:

- Multi-stage builds for smaller images
- BuildKit caching for faster builds
- Non-root user for security
- Optimized layer caching

## 🧪 Testing

### Run Tests

```bash
make test              # Run all tests
make test-coverage     # Run with coverage report
pytest -v              # Verbose output
pytest tests/unit/     # Run specific test directory
```

### Database Testing

Database projects use testcontainers for isolated testing:

- Automatic PostgreSQL container setup
- Database migrations applied before tests
- Rollback after each test for isolation

## 🔧 GitHub Actions

When enabled, projects include:

- **Pull Request checks**: Linting and testing
- **Main branch checks**: Full test suite
- **Matrix testing**: Multiple Python versions
- **Database services**: PostgreSQL for database projects

## 📁 Project Structure

```
your-project/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── core/
│   │   ├── config.py             # Settings management
│   │   ├── database.py           # Database config (db projects)
│   │   └── ...
│   ├── models/                   # SQLAlchemy models (db projects)
│   │   └── example.py
│   └── api/                      # FastAPI routes (FastAPI projects)
│       ├── examples/
│       └── health_checks/
├── tests/
│   ├── conftest.py               # Test configuration
│   ├── api/                      # API tests (FastAPI projects)
│   └── unit/                     # Unit tests
├── migrations/                   # Alembic migrations (db projects)
├── docker-compose.yaml           # Database services (db projects)
├── Dockerfile                    # Multi-stage build
├── pyproject.toml               # Dependencies and config
├── Makefile                     # Common commands
└── .env                         # Environment variables
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different project types:
   ```bash
   cookiecutter . --no-input project_type=fastapi_db
   cookiecutter . --no-input project_type=cli_slim
   ```
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
