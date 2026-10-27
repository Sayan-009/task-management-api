FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONPATH=/app/src

# Install third-party dependencies first
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code and migration files
COPY src/ ./src/
COPY alembic/ ./alembic/

# Copy this only if alembic.ini exists at your project root
COPY alembic.ini ./

EXPOSE 8000

CMD ["uv", "run", "--no-sync", "uvicorn", "task_management_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
