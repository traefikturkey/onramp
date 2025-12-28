# Environment Variables Reference

OnRamp uses a modular environment system with variables organized by purpose.

## File Locations

| File | Purpose |
|------|---------|
| `services-enabled/.env` | Core configuration (domain, Cloudflare, timezone) |
| `services-enabled/.env.nfs` | NFS mount paths for media services |
| `services-enabled/.env.external` | External service URLs |
| `services-enabled/<service>.env` | Service-specific overrides |
| `services-enabled/custom.env` | Custom/unmapped variables |

## Core Variables (.env)

### Required

```bash
# Your domain name
HOST_DOMAIN=example.com

# Hostname of this server
HOST_NAME=myserver

# Cloudflare credentials
CF_API_EMAIL=your-email@example.com
CF_DNS_API_TOKEN=your-api-token
```

### System

```bash
# Timezone (TZ database format)
TZ=America/New_York

# User/Group IDs for file permissions
PUID=1000
PGID=1000

# Host IP address (auto-detected if not set)
HOSTIP=192.168.1.100
```

### Traefik

```bash
# Traefik dashboard hostname
TRAEFIK_HOST_NAME=traefik

# Log level (DEBUG, INFO, WARN, ERROR)
TRAEFIK_LOG_LEVEL=ERROR
```

## NFS Variables (.env.nfs)

For services using NFS-mounted storage:

```bash
# Media paths
NFS_MOVIES=/mnt/nfs/movies
NFS_TV=/mnt/nfs/tv
NFS_MUSIC=/mnt/nfs/music
NFS_DOWNLOADS=/mnt/nfs/downloads
```

## External Services (.env.external)

For connecting to services on other hosts:

```bash
# Example external service
EXTERNAL_PLEX_ADDRESS=192.168.1.50:32400
```

## Service-Specific Variables

Each service can have its own variables. Common patterns:

```bash
# Docker image tag
<SERVICE>_DOCKER_TAG=latest

# Container name
<SERVICE>_CONTAINER_NAME=servicename

# Restart policy
<SERVICE>_RESTART=unless-stopped

# Memory limit
<SERVICE>_MEM_LIMIT=2g

# Traefik hostname
<SERVICE>_HOST_NAME=servicename

# Enable/disable Traefik routing
<SERVICE>_TRAEFIK_ENABLED=true

# Enable/disable Watchtower updates
<SERVICE>_WATCHTOWER_ENABLED=true
```

### Example: Plex

```bash
PLEX_DOCKER_TAG=latest
PLEX_CONTAINER_NAME=plex
PLEX_HOST_NAME=plex
PLEX_CLAIM=claim-xxxx
PLEX_TRAEFIK_ENABLED=true
```

## How Environment Variables Are Loaded

OnRamp uses two mechanisms for environment variables, each serving different purposes:

### 1. Makefile `--env-file` Flags (YAML Parsing)

The Makefile loads ALL env files via `--env-file` flags to docker compose:

```makefile
ENV_FILES := .env .env.nfs .env.external *.env
ENV_FLAGS := $(foreach file, $(ENV_FILES), --env-file $(file))
```

This enables **YAML variable substitution** - variables like `${SERVICE_DOCKER_TAG:-latest}` in your docker-compose files are resolved at parse time. Without this, values like `container_name` and labels wouldn't work.

### 2. YAML `env_file:` Directive (Container Runtime)

Each service YAML explicitly declares its env file:

```yaml
services:
  myservice:
    image: myservice:${MYSERVICE_DOCKER_TAG:-latest}
    env_file:
      - ./services-enabled/myservice.env
    container_name: ${MYSERVICE_CONTAINER_NAME:-myservice}
```

This serves two purposes:
- **Runtime Environment**: Provides variables inside the running container
- **Self-Documentation**: Reading the YAML shows exactly which env file the service uses

### Why Both Are Needed

| Mechanism | When It Runs | What It Does |
|-----------|--------------|--------------|
| `--env-file` (Makefile) | YAML parsing | Resolves `${VAR}` in container_name, labels, volumes |
| `env_file:` (YAML) | Container start | Provides vars inside the container |

Example: `SYNCTHING_CONTAINER_NAME=sync` must be available during YAML parsing for `container_name: ${SYNCTHING_CONTAINER_NAME:-syncthing}` to resolve correctly.

## Variable Precedence

Variables are loaded in this order (later overrides earlier):

1. `services-enabled/.env` (base)
2. `services-enabled/.env.nfs` (NFS paths)
3. `services-enabled/.env.external` (external services)
4. `services-enabled/<service>.env` (service-specific)
5. `services-enabled/custom.env` (custom overrides)

## Default Values

Services use default values if variables aren't set:

```yaml
# In service yml file
image: service:${SERVICE_DOCKER_TAG:-latest}
#                                  ^^^^^^^ default value
```

## Editing Environment Files

```bash
# Edit main environment
make edit-env-onramp

# Edit NFS paths
make edit-env-nfs

# Edit external services
make edit-env-external

# Edit service-specific
make edit-env servicename

# Edit custom variables
make edit-env-custom
```

## Validating Configuration

Check required variables are set:

```bash
make check-cf        # Cloudflare variables
make check-authentik # Authentik variables
make check-authelia  # Authelia variables
```
