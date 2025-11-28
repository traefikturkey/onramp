FROM python:3.14-slim

LABEL maintainer="OnRamp Project"
LABEL description="Tool container for OnRamp scaffolding and dashboard"

# Install uv from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install system dependencies:
# - gettext-base: provides envsubst for template rendering
# - openssl: for RSA key generation (geopulse)
# - wget: for downloading files (radarr/sonarr arr-scripts)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gettext-base \
        openssl \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project files for dependency installation
COPY pyproject.toml ./

# Install Python dependencies with uv (without installing the project itself)
RUN uv sync --no-dev --no-install-project

# Copy scripts and tests
COPY scripts/ /scripts/
COPY tests/ /app/tests/

# Copy dashboard application
COPY dashboard/ /dashboard/

# Make scripts executable and create symlink for pytest
RUN chmod +x /scripts/*.py && \
    ln -s /scripts /app/scripts

# Set Python path to find dashboard module
ENV PYTHONPATH=/

# Expose dashboard port
EXPOSE 8000

# Default command: run dashboard using the venv python directly
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "dashboard.app:app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
