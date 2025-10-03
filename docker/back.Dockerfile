# ===========================
# Backend build stage
# ===========================
FROM 3.12.0-slim-bullseye AS backend-build

WORKDIR /app

# Install uv package manager
RUN pip install uv

# Copy lockfiles first to leverage caching
COPY back/pyproject.toml back/uv.lock ./

# Install Python dependencies
RUN uv sync --no-cache --no-dev --no-install-project

# Copy the rest of the backend code
COPY back/ ./


# ===========================
# Final runtime image
# ===========================
FROM python:3.12.0-slim-bullseye

WORKDIR /app

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"

# Copy Python virtual environment from backend build
COPY --from=backend-build /app/.venv ./.venv

# Copy backend application
COPY --from=backend-build /app/src/template_app ./template_app
COPY --from=backend-build /app/alembic ./alembic
COPY --from=backend-build /app/alembic.ini ./alembic.ini

CMD ["python", "-m", "template_app.main"]
