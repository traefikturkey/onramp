FROM python:3.12-slim

LABEL maintainer="OnRamp Project"
LABEL description="Tool container for OnRamp scaffolding and migration"

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

# Install Python dependencies
RUN pip install --no-cache-dir pyyaml

# Create app directory
WORKDIR /app

# Copy scripts
COPY scripts/ /scripts/

# Make scripts executable
RUN chmod +x /scripts/*.py

# Default command shows help
CMD ["python", "/scripts/scaffold.py", "--help"]
