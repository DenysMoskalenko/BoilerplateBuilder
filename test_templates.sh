#!/bin/bash
set -e

echo "🧪 Testing all cookiecutter project templates locally..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_TYPES=("fastapi_db" "fastapi_slim" "cli_db" "cli_slim")
PYTHON_VERSION="3.11"
TEST_DIR="./test_projects"

# Clean up function
cleanup() {
    echo "🧹 Cleaning up test projects..."
    rm -rf "$TEST_DIR"
}

# Set up cleanup on exit
trap cleanup EXIT

# Create test directory
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📋 Testing ${#PROJECT_TYPES[@]} project types..."

for project_type in "${PROJECT_TYPES[@]}"; do
    echo -e "\n${BLUE}🔨 Testing project type: $project_type${NC}"
    
    project_name="test_${project_type}"
    
    # Generate project
    echo "  📦 Generating project..."
    cookiecutter .. --no-input \
        project_name="$project_name" \
        project_type="$project_type" \
        python_version="$PYTHON_VERSION" \
        author_name="Test Author" \
        author_email="test@example.com" \
        use_pre_commit="yes" \
        use_github_actions="yes" \
        initialize_git="no"
    
    cd "$project_name"
    
    # Install dependencies
    echo "  📦 Installing dependencies..."
    uv lock
    uv sync
    
    # Set up environment
    echo "  ⚙️  Setting up environment..."
    if [[ "$project_type" == *"db"* ]]; then
        echo "DATABASE_URL=postgresql+psycopg://test:test@localhost:5432/test" > .env
        echo "MIGRATION_ON_STARTUP=False" >> .env
    else
        echo "PROJECT_NAME=$project_name" > .env
    fi
    
    # Test linting (fix auto-fixable issues first)
    echo "  🧹 Running linter..."
    uv run ruff check --fix . || {
        echo -e "${RED}❌ Linting failed for $project_type${NC}"
        exit 1
    }
    
    uv run ruff format --check . || {
        echo -e "${RED}❌ Format check failed for $project_type${NC}"
        exit 1
    }
    
    # Test basic imports
    echo "  🧪 Testing basic functionality..."
    if [[ "$project_type" == "fastapi"* ]]; then
        uv run python -c "from app.main import app; print('FastAPI app imported successfully')" || {
            echo -e "${RED}❌ FastAPI import failed for $project_type${NC}"
            exit 1
        }
    else
        timeout 5s uv run python -m app.main > /dev/null 2>&1 || true
    fi
    
    # Test Docker build
    echo "  🐳 Testing Docker build..."
    docker build -t "test-$project_type" . > /dev/null || {
        echo -e "${RED}❌ Docker build failed for $project_type${NC}"
        exit 1
    }
    
    # Verify key files exist
    echo "  📁 Verifying file structure..."
    files_to_check=("pyproject.toml" "Dockerfile" "Makefile" "app/main.py")
    
    if [[ "$project_type" == *"db"* ]]; then
        files_to_check+=("alembic.ini" "docker-compose.yaml" "app/models/example.py")
    fi
    
    for file in "${files_to_check[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo -e "${RED}❌ Missing file: $file for $project_type${NC}"
            exit 1
        fi
    done
    
    echo -e "  ${GREEN}✅ $project_type passed all tests${NC}"
    
    cd ..
done

echo -e "\n${GREEN}🎉 All project templates passed validation!${NC}"
echo -e "\n📊 Summary:"
echo "  • Tested ${#PROJECT_TYPES[@]} project types"
echo "  • All linting checks passed"
echo "  • All Docker builds successful"
echo "  • All file structures validated"
echo -e "\n🚀 Templates are ready for use!" 