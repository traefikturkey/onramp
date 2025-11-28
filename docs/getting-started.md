# Getting Started with OnRamp

OnRamp is a Docker-based self-hosted services platform using Traefik as a reverse proxy with automatic SSL certificates via Cloudflare DNS.

## Prerequisites

- Linux server (Debian/Ubuntu recommended)
- Docker and Docker Compose installed
- Domain name configured with Cloudflare DNS
- Cloudflare API token with Zone:DNS:Edit permissions

## Quick Start

### 1. Clone the Repository

```bash
sudo mkdir -p /apps
sudo chown -R $USER:$USER /apps
cd /apps
git clone https://github.com/traefikturkey/onramp.git
cd onramp
```

### 2. Initial Setup

```bash
make install
```

This will:
- Install required dependencies
- Create the initial environment configuration
- Open your editor to configure essential variables

### 3. Configure Environment

Edit `services-enabled/.env` with your settings:

```bash
# Required
HOST_DOMAIN=yourdomain.com
HOST_NAME=yourserver
CF_API_EMAIL=your-cloudflare-email@example.com
CF_DNS_API_TOKEN=your-cloudflare-api-token

# Optional but recommended
TZ=America/New_York
PUID=1000
PGID=1000
```

### 4. Test with Staging Certificates

```bash
make start-staging
```

This uses Let's Encrypt staging certificates to verify your setup without hitting rate limits.

### 5. Start Production

Once staging works:

```bash
make down-staging
make start
```

## Enabling Services

List available services:
```bash
make list-services
```

Enable a service:
```bash
make enable-service servicename
make start-service servicename
```

Disable a service:
```bash
make disable-service servicename
```

## Common Commands

| Command | Description |
|---------|-------------|
| `make` | Start all enabled services |
| `make down` | Stop all services |
| `make restart` | Restart all services |
| `make logs` | View logs |
| `make update` | Pull latest images and restart |
| `make help` | Show all available commands |

## Next Steps

- See [Scaffolding](scaffolding.md) for adding service configurations
- See [Troubleshooting](troubleshooting.md) for common issues
- See [Environment Variables](env-vars.md) for configuration reference
