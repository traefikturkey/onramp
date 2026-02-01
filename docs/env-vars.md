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

Environment variables are resolved in a three-tier hierarchy, with later files overriding earlier ones:

### Priority Levels

**1. Global Defaults (Lowest Priority)**
```
services-enabled/.env
```
Base configuration loaded first. Contains core variables like `HOST_DOMAIN`, `HOST_NAME`, `TZ`, `PUID`, `PGID`.

**2. Special-Purpose Files (Middle Priority)**
```
services-enabled/.env.nfs
services-enabled/.env.external
services-enabled/custom.env
```
Loaded after global defaults. NFS paths, external service URLs, and custom unmapped variables. Later files override earlier ones.

**3. Service-Specific Configuration (Highest Priority)**
```
services-enabled/<service>.env
```
Always wins over global and special-purpose files. Each service's individual overrides take precedence.

### Override Behavior

If the same variable is defined in multiple files, the priority order determines which value is used:
- Service-specific `.env` overrides all others
- Special-purpose files (`.env.nfs`, `.env.external`, `custom.env`) override global `.env`
- Global `.env` provides fallbacks for any undefined variables

**Example:** If `TRAEFIK_LOG_LEVEL=INFO` in `services-enabled/.env` but `TRAEFIK_LOG_LEVEL=DEBUG` in `services-enabled/traefik.env`, the service-specific value (`DEBUG`) will be used.

## Archive System

When services are disabled, their environment configurations are preserved in an archive system to protect sensitive data and customizations across disable/enable cycles.

### How Archiving Works

When you disable a service:
- Its `.env` file is moved to `services-enabled/archive/<service>.env`
- All variables (passwords, API keys, custom settings) are preserved
- When you re-enable the service, the scaffolder prompts to restore the archived configuration
- This ensures sensitive data like database passwords and API tokens aren't lost

### Manual Archive Operations

```bash
# Archive a service's current environment
services.py archive-env SERVICE

# Restore a service's environment from archive
services.py restore-env SERVICE

# Check the status of archived files
services.py check-archive SERVICE
```

### Archive Directory Structure

```
services-enabled/
├── archive/
│   ├── plex.env          # Archived when disabled
│   ├── jellyfin.env      # Archived when disabled
│   └── paperless.env     # Archived when disabled
├── plex.env              # Current (active services only)
└── jellyfin.env
```

### Use Cases

- **Temporary Service Disabling**: Archive preserves settings when you disable a service temporarily
- **Experimentation**: Re-enable with original config without manual reconfiguration
- **Password/Key Management**: Sensitive credentials are never lost
- **Quick Recovery**: Restore exact configuration without remembering custom values

## Auto-Generation

The scaffolder ensures all services have a working environment file, even without explicit configuration.

### How It Works

When you enable a service, the scaffolder checks for a `services-scaffold/<service>/env.template`:

- **If template exists**: Generates `services-enabled/<service>.env` from the template with variable substitution
- **If no template**: Creates a minimal `services-enabled/<service>.env` automatically
- This ensures the YAML `env_file:` directive always finds its file

### Automatically Generated File Format

For services without a scaffold template, an auto-generated `.env` looks like:

```bash
# Auto-generated for SERVICE
# Created: 2024-01-15 10:30:00
#
# This file can be customized with service-specific variables.
# For details, see docs/env-vars.md

SERVICE_DOCKER_TAG=latest
SERVICE_CONTAINER_NAME=service
SERVICE_TRAEFIK_ENABLED=true
```

### Benefits

- **No Boilerplate Required**: Services work immediately without requiring scaffold templates
- **Flexible Customization**: Generated files can be edited to add service-specific variables
- **Consistent Behavior**: All services follow the same env file pattern
- **Self-Documenting**: Headers indicate the file was auto-generated and can be customized

### Creating Custom Templates

To replace auto-generation with custom configuration:

1. Create `services-scaffold/<service>/env.template`
2. Use `${VARIABLE_NAME}` for variable substitution
3. Re-run `make scaffold-build <service>` to regenerate

The custom template will then override auto-generation for that service.

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
