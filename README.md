# Python Project Boilerplate Builder 🏗️

A modern cookiecutter template for generating Python projects with FastAPI or CLI applications, including database
support, Docker, testing, and CI/CD setup.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- [cookiecutter](https://github.com/cookiecutter/cookiecutter)

### Installation


Install cookiecutter
```bash
pip install cookiecutter
# or
uv add cookiecutter
```
Generate a new project
```
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

### Observability Features (Optional)

- 📊 **OpenTelemetry** distributed tracing
- 📈 **Prometheus** metrics with custom business metrics
- 📝 **Structured JSON logging** with trace correlation
- 🔍 **Local development stack** with Grafana, Tempo, Loki, and Promtail
- 📊 **Pre-built Grafana dashboards** tailored to your project type
- 🎯 **Easy-to-use decorators** for instrumenting your code

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
- **Python version**: 3.11, 3.12, or 3.13
- **Use observability**: Add OpenTelemetry tracing, Prometheus metrics, and structured logging
- **Use local telemetry stack**: Include local Grafana/Tempo/Prometheus/Loki stack for development
  - ⚠️ **Note**: `generate_local_otel_stack` requires `use_otel_observability` to be enabled. If you select `use_otel_observability=no`, the project generation will fail with a clear error message.
  - 💡 **Tip**: If you encounter a "directory already exists" error, it may be from a previous failed generation. Remove the directory and try again: `rm -rf YourProjectName`
- **Pre-commit hooks**: Enable/disable pre-commit
- **GitHub Actions**: Enable/disable CI/CD
- **Git initialization**: Auto-initialize git repo

### Non-Interactive Generation

```bash
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder \
  --no-input \
  extract_to_current_dir="Create New" \
  project_name="MyAwesomeAPI" \
  project_type="fastapi_db" \
  author_name="John Doe" \
  author_email="john@example.com"
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

## 📊 Observability

### What's Included

When you enable observability, your project gets:

1. **Distributed Tracing** with OpenTelemetry
   - Automatic instrumentation for FastAPI routes
   - SQLAlchemy query tracing (for database projects)
   - Custom span creation support

2. **Prometheus Metrics**
   - HTTP request metrics (FastAPI projects)
   - Custom business metrics with easy-to-use decorators
   - Example metrics based on your project type

3. **Structured JSON Logging**
   - Trace and span ID correlation
   - Compatible with Grafana Loki
   - Easy to parse and query

### Local Development Stack

⚠️ **Important**: The local telemetry stack (`generate_local_otel_stack`) requires observability to be enabled (`use_otel_observability=yes`). If you try to generate a project with `use_otel_observability=no` and `generate_local_otel_stack=yes`, the generation will fail with a clear error message.

If you enable the local telemetry stack, you get a full observability setup with:

- **Grafana** (http://localhost:3000) - Visualization and dashboards
- **Tempo** - Distributed tracing backend
- **Prometheus** - Metrics collection
- **Loki** - Log aggregation
- **OTEL Collector** - Telemetry data pipeline

### Quick Start with Observability

```bash
# Generate project with observability
cookiecutter https://github.com/DenysMoskalenko/BoilerplateBuilder \
  --no-input \
  project_name="MyObservableAPI" \
  project_type="fastapi_db" \
  use_otel_observability="yes" \
  generate_local_otel_stack="yes"

cd MyObservableAPI

# Start the full stack
docker-compose up -d

# Access dashboards
# Grafana: http://localhost:3000 (no login required)
# Prometheus: http://localhost:9090
# Tempo: http://localhost:3200
```

### Instrumenting Your Code

The template includes helper decorators for easy instrumentation:

```python
from app.observability.metrics import counters, gauges
from app.observability.metrics.primitives import increment_after, track_inflight

# Track in-flight operations
@track_inflight(gauges.my_gauge.labels('operation_name'))
async def my_operation():
    pass

# Count operation completions
@increment_after(counters.my_counter.labels('operation', 'success'))
async def my_operation():
    pass
```

### Production Deployment

For production, configure the OTLP endpoint to point to your observability backend:

```bash
OBSERVABILITY_OTLP_GRPC_ENDPOINT=grpc://your-otel-collector:4317
OBSERVABILITY_TRACING_ENABLED=True
OBSERVABILITY_METRICS_ENABLED=True
OBSERVABILITY_LOGS_IN_JSON=True
OBSERVABILITY_TRACING_SAMPLE_RATE_PERCENT=10  # Sample 10% of traces
```

Compatible with: Grafana Cloud, Datadog, New Relic, Honeycomb, and any OTLP-compatible backend.

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

## ✅ Template Smoke Tests

Validate every project type (including lint + test runs) after template changes with the helper script:

```bash
python -m scripts.template_smoke_test
```

Useful flags:

- `--project-types fastapi_db cli_db` – run a subset.
- `--use-otel yes` – exercise the observability code paths (required when pairing with `--local-otel-stack yes`).
- `--keep-builds` – keep the generated projects for inspection; by default they are cleaned up.

The script generates each requested project without initializing git, runs `uv sync`, and then executes `uv run make lint` and `uv run make test` inside the project. Builds land under `.template-builds/<timestamp>/…`; pass `--run-id=my-run` to control the folder name.

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
