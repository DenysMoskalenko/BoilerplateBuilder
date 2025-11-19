# Stage 1: Build stage
FROM python:{{ cookiecutter.python_version }}-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# Stage 2: Runtime stage (use a final image without uv)
FROM python:{{ cookiecutter.python_version }}-slim AS runner

WORKDIR /app

# Create dedicated non-root user for the runtime image
RUN addgroup --system app \
    && adduser --system --ingroup app --home /app app

# Copy the application from the builder with proper ownership
COPY --from=builder --chown=app:app /app /app

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Drop root privileges for the app process
USER app

{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_slim"] %}
ENTRYPOINT ["python", "-m", "app.main"]
# Use gunicorn for scale into several processes (workers) instead of uvicorn if needed
#ENTRYPOINT ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-"]
{%- else %}
ENTRYPOINT ["python", "-m", "app.main"]
{%- endif %}
