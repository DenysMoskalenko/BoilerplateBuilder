# Python Project Boilerplate Builder 🏗️

A modern cookiecutter template for generating Python projects with FastAPI or CLI applications, including database support, Docker, testing, and CI/CD setup.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)
- [cookiecutter](https://github.com/cookiecutter/cookiecutter)

### Installation

```bash
# Install cookiecutter
pip install cookiecutter
# or
uv add cookiecutter

# Generate a new project
cookiecutter https://github.com/your-username/BoilerplateBuilder
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

## 📖 Usage

### Interactive Generation

```bash
cookiecutter https://github.com/your-username/BoilerplateBuilder
```

You'll be prompted for:
- **Project name**: Your project name
- **Project description**: Brief description
- **Author name**: Your name
- **Author email**: Your email
- **Project type**: Choose from `fastapi_db`, `fastapi_slim`, `cli_db`, `cli_slim`
- **Python version**: 3.10, 3.11, or 3.12
- **Pre-commit hooks**: Enable/disable pre-commit
- **GitHub Actions**: Enable/disable CI/CD
- **Git initialization**: Auto-initialize git repo

### Non-Interactive Generation

```bash
cookiecutter https://github.com/your-username/BoilerplateBuilder \
  --no-input \
  project_name="MyAwesomeAPI" \
  project_type="fastapi_db" \
  author_name="John Doe" \
  author_email="john@example.com"
```

## 🏃‍♂️ Getting Started with Generated Project

### 1. Enter your project directory
```bash
cd your-project-name
```

### 2. Set up environment
```bash
# Install dependencies (done automatically during generation)
uv sync

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings
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
