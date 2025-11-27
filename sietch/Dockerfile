FROM python:3.12-slim

LABEL maintainer="OnRamp Project"
LABEL description="Tool container for OnRamp scaffolding and migration"

# Install envsubst (from gettext-base)
RUN apt-get update && \
    apt-get install -y --no-install-recommends gettext-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy scripts
COPY scripts/ /scripts/

# Make scripts executable
RUN chmod +x /scripts/*.py

# Default command shows help
CMD ["python", "/scripts/scaffold.py", "--help"]
