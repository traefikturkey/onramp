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

# Install Python dependencies from requirements.txt
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Create app directory
WORKDIR /app

# Copy scripts
COPY scripts/ /scripts/

# Copy dashboard application
COPY dashboard/ /dashboard/

# Make scripts executable
RUN chmod +x /scripts/*.py

# Expose dashboard port
EXPOSE 8000

# Default command: run dashboard
# For scripts-only mode, override with: CMD ["python", "/scripts/scaffold.py", "--help"]
CMD ["uvicorn", "dashboard.app:app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
