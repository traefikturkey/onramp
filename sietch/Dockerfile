FROM python:3.12-slim

LABEL maintainer="OnRamp Project"
LABEL description="Tool container for OnRamp scaffolding and migration"

# Install uv
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

# Copy project files and install dependencies
COPY pyproject.toml ./
RUN uv sync

# Copy scripts and tests
COPY scripts/ /scripts/
COPY tests/ /app/tests/

# Make scripts executable and create symlink for pytest
RUN chmod +x /scripts/*.py && \
    ln -s /scripts /app/scripts

# Default command shows help
CMD ["uv", "run", "python", "/scripts/scaffold.py", "--help"]
