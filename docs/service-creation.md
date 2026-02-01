# Service Creation Guide

This guide walks through creating a new service for OnRamp, from initial template to production-ready configuration.

## Table of Contents

1. [Creating from Template](#creating-from-template)
2. [Required YAML Elements](#required-yaml-elements)
3. [Auto-generating env.template](#auto-generating-envtemplate)
4. [Service Config Versioning](#service-config-versioning)
5. [Linting Services](#linting-services)
6. [Upgrading Outdated Services](#upgrading-outdated-services)
7. [Complete Example](#complete-example)

## Creating from Template

OnRamp provides a template system to quickly scaffold new services.

### Generate from Template

```bash
make create-service SERVICE=myservice
```

This generates `services-available/myservice.yml` from the template and opens it in your editor.

**For game servers:**
```bash
make create-game SERVICE=mygame
```

### Template Structure

The generated template includes:

```yaml
networks:
  traefik:
    external: true

# description: <= put a brief description here =>
# <================= add links to dockerhub or github repo here =================>

services:
  myservice:
    image: <==== container_image ====>:${MYSERVICE_DOCKER_TAG:-latest}
    container_name: ${MYSERVICE_CONTAINER_NAME:-myservice}
    restart: ${MYSERVICE_RESTART:-unless-stopped}
    mem_limit: ${MYSERVICE_MEM_LIMIT:-200g}
    networks:
      - traefik
    volumes:
      - ./etc/myservice:/config
      - /etc/localtime:/etc/localtime:ro
    environment:
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
      - TZ=${TZ}
    labels:
      - joyride.host.name=${MYSERVICE_HOST_NAME:-myservice}.${HOST_DOMAIN}
      - traefik.enable=${MYSERVICE_TRAEFIK_ENABLED:-true}
      - traefik.http.routers.myservice.entrypoints=websecure
      - traefik.http.routers.myservice.rule=Host(`${MYSERVICE_HOST_NAME:-myservice}.${HOST_DOMAIN}`)
      - traefik.http.services.myservice.loadbalancer.server.port=8096
      - com.centurylinklabs.watchtower.enable=${MYSERVICE_WATCHTOWER_ENABLED:-true}
      - autoheal=${MYSERVICE_AUTOHEAL_ENABLED:-true}
```

### What to Edit

1. **Image**: Replace `<==== container_image ====>` with actual image name
2. **Description**: Add single-sentence description
3. **Links**: Add GitHub or Docker Hub URLs
4. **Volumes**: Adjust paths to match container requirements
5. **Port**: Update `loadbalancer.server.port` to match container's web port
6. **Labels**: Remove unused Traefik labels if not a web service

## Required YAML Elements

Every service YAML must include these elements to meet OnRamp standards.

### Documentation Header

```yaml
# config_version: 2
# description: Single sentence describing what this service does
# https://github.com/owner/repo
# https://hub.docker.com/r/owner/image
```

**Key points:**
- `config_version: 2` marks it as using current standards (v1 is legacy)
- Description should be concise (shown in service lists)
- Include at least one URL reference (GitHub or Docker Hub)

### Network Configuration

```yaml
networks:
  traefik:
    external: true
```

**Exceptions:** Services using `network_mode: host` don't need this.

### Service Name Variables

Use variables with the service name prefix (uppercase, underscores):

```yaml
services:
  myservice:
    image: owner/image:${MYSERVICE_DOCKER_TAG:-latest}
    container_name: ${MYSERVICE_CONTAINER_NAME:-myservice}
    restart: ${MYSERVICE_RESTART:-unless-stopped}
```

**Naming convention:** `${SERVICENAME_PURPOSE:-default}`

### Volume Mounts

Store configuration in `etc/` or data in `media/`:

```yaml
volumes:
  - ./etc/myservice:/config           # Configuration files
  - ./media/myservice:/data           # Application data
  - /etc/localtime:/etc/localtime:ro  # Required if using TZ env var
```

### Environment Variables

```yaml
environment:
  - PUID=${PUID:-1000}
  - PGID=${PGID:-1000}
  - TZ=${TZ}
```

**Skip PUID/PGID for:** Database containers (postgres, mariadb, redis) and infrastructure services (traefik, watchtower, prometheus).

### Env File Directive

**Every service must include:**

```yaml
env_file:
  - ./services-enabled/myservice.env
```

This loads service-specific variables into the container at runtime.

### Traefik Labels (Web Services)

For services with web interfaces:

```yaml
labels:
  - joyride.host.name=${MYSERVICE_HOST_NAME:-myservice}.${HOST_DOMAIN}
  - traefik.enable=${MYSERVICE_TRAEFIK_ENABLED:-true}
  - traefik.http.routers.myservice.entrypoints=websecure
  - traefik.http.routers.myservice.rule=Host(`${MYSERVICE_HOST_NAME:-myservice}.${HOST_DOMAIN}`)
  - traefik.http.services.myservice.loadbalancer.server.port=8080
  - com.centurylinklabs.watchtower.enable=${MYSERVICE_WATCHTOWER_ENABLED:-true}
  - autoheal=${MYSERVICE_AUTOHEAL_ENABLED:-true}
```

**Critical:** The port in `loadbalancer.server.port` must match the container's actual web port.

### For HTTPS Backends

If the container serves HTTPS internally:

```yaml
- traefik.http.services.myservice.loadbalancer.server.scheme=https
```

### Non-Web Services

Services without web interfaces still need:

```yaml
labels:
  - com.centurylinklabs.watchtower.enable=${MYSERVICE_WATCHTOWER_ENABLED:-true}
  - autoheal=${MYSERVICE_AUTOHEAL_ENABLED:-false}
```

Set `autoheal=false` or omit it for services without healthchecks.

### Healthchecks

If enabling autoheal, define a healthcheck:

```yaml
healthcheck:
  test: ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1']
  interval: 60s
  timeout: 10s
  retries: 3
  start_period: 30s
labels:
  - autoheal=${MYSERVICE_AUTOHEAL_ENABLED:-true}
```

**Without healthcheck:** Set `autoheal=false` or autoheal won't function.

## Auto-generating env.template

OnRamp can automatically extract environment variables from your compose YAML and generate an `env.template` scaffold.

### Create env.template

```bash
make create-scaffold-env SERVICE=myservice
```

This:
1. Scans `services-available/myservice.yml` for `${MYSERVICE_*}` variables
2. Groups variables by purpose (Docker, Network, Paths, Secrets, etc.)
3. Creates `services-scaffold/myservice/env.template`
4. Preserves default values from `${VAR:-default}` patterns

### Preview Without Creating

```bash
make create-scaffold-env-dry-run SERVICE=myservice
```

Shows what would be generated without writing files.

### What Gets Extracted

The EnvExtractor scans for:
- Image tags: `${MYSERVICE_DOCKER_TAG:-latest}`
- Container names: `${MYSERVICE_CONTAINER_NAME:-myservice}`
- Hostnames: `${MYSERVICE_HOST_NAME:-myservice}`
- Ports: `${MYSERVICE_PORT:-8080}`
- Feature flags: `${MYSERVICE_TRAEFIK_ENABLED:-true}`
- Secrets: `${MYSERVICE_PASSWORD}`, `${MYSERVICE_TOKEN}`
- Custom variables: Anything starting with `MYSERVICE_`

**Skipped variables:** Global variables like `PUID`, `PGID`, `TZ`, `HOST_DOMAIN`, `HOST_NAME` are not included in service-specific env files.

### Generated Template Format

```bash
###############################################
# Myservice Configuration
#
# Generated from services-scaffold/myservice/env.template
# To regenerate: make scaffold-build myservice
###############################################

# Docker image settings
MYSERVICE_DOCKER_TAG=${MYSERVICE_DOCKER_TAG:-latest}

# Container settings
MYSERVICE_CONTAINER_NAME=${MYSERVICE_CONTAINER_NAME:-myservice}
MYSERVICE_RESTART=${MYSERVICE_RESTART:-unless-stopped}

# Network settings
MYSERVICE_HOST_NAME=${MYSERVICE_HOST_NAME:-myservice}
MYSERVICE_PORT=${MYSERVICE_PORT:-8080}

# Secrets and credentials
MYSERVICE_ADMIN_PASSWORD=${MYSERVICE_ADMIN_PASSWORD}

# Feature flags
MYSERVICE_TRAEFIK_ENABLED=${MYSERVICE_TRAEFIK_ENABLED:-true}
MYSERVICE_WATCHTOWER_ENABLED=${MYSERVICE_WATCHTOWER_ENABLED:-true}
```

### Variable Grouping

Variables are automatically grouped:

| Group | Triggers |
|-------|----------|
| Docker | `docker_tag` |
| Container | `container_name`, `restart` |
| Network | `host_name`, `port` |
| Paths | `path`, `dir`, `media` |
| Secrets | `password`, `secret`, `token`, `key` |
| Connection | `url`, `instance` |
| Runner | `label` (for CI runners) |
| Features | `enabled` |
| Config | Everything else |

### Manual Editing

After generation, edit the template to:
- Add comments explaining complex variables
- Group related variables
- Add validation hints (e.g., "Must be 32 characters")
- Remove variables that should remain in the YAML

## Service Config Versioning

OnRamp uses config versioning to track service standards.

### Version Metadata

Add to the top of your YAML:

```yaml
# config_version: 2
```

### Version Standards

**v1 (Legacy):**
- Basic Traefik labels
- May have inconsistent variable naming
- Missing autoheal or watchtower labels

**v2 (Current):**
- Consistent `${SERVICE_*}` variable naming
- Required labels: `joyride.host.name`, `autoheal`, `watchtower.enable`
- `env_file:` directive pointing to service env
- Healthcheck if `autoheal=true`
- PUID/PGID for user services
- TZ + `/etc/localtime` mount

### Checking Version

```bash
# Via services.py
make sietch-build
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py check-version myservice

# Via lint
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint myservice
```

## Linting Services

The linter validates services against OnRamp standards.

### Lint Single Service

```bash
# In sietch container
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint myservice
```

Output:
```
Linting: myservice
Valid: True

Warnings:
  - myservice: Missing watchtower.enable label
```

### Lint All Services

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint --all
```

### Lint Only Enabled Services

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint --all --enabled
```

### Strict Mode

Treats warnings as errors:

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint myservice --strict
```

### Auto-fix Capability

Some linting issues can be auto-fixed:

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint myservice --fix
```

**Note:** Auto-fix is currently limited. Most issues require manual correction.

### What the Linter Checks

**Documentation:**
- `# description:` comment present
- URL references (GitHub, Docker Hub)

**Config Version:**
- Version specified
- Using current version (v2)

**Networks:**
- Traefik network defined (unless using `network_mode: host`)

**Environment Variables:**
- PUID/PGID present (for non-infrastructure services)
- TZ present
- `/etc/localtime` mount if TZ is set

**Labels (Web Services):**
- `joyride.host.name` label
- `traefik.enable` label
- `traefik.http.routers.*` configuration
- `traefik.http.services.*.loadbalancer.server.port` set
- Port matches container's actual port

**Labels (All Services):**
- `com.centurylinklabs.watchtower.enable` label
- `autoheal` label
- If `autoheal=true`, healthcheck must be defined

**Volumes:**
- `/etc/localtime:/etc/localtime:ro` if TZ is set

**Hardcoded Values:**
- Detects hardcoded hostnames (should use variables)

### Common Linting Errors

**Missing healthcheck with autoheal:**
```
Error: myservice: autoheal=true without healthcheck (autoheal won't work)
```

**Fix:** Add healthcheck or set `autoheal=false`

**Outdated config version:**
```
Error: Outdated config version: v1 (current standard: v2)
```

**Fix:** Add `# config_version: 2` and update labels to v2 standards

**Missing required labels:**
```
Error: myservice: Web service missing joyride.host.name label
```

**Fix:** Add label to web services

## Upgrading Outdated Services

Services marked as v1 should be upgraded to v2 standards.

### Identify Outdated Services

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint --all --outdated
```

Output:
```
Services with outdated config (v1):
  - oldservice
  - anotheroldservice

Linting: oldservice
Valid: False
Errors:
  - Outdated config version: v1 (current standard: v2)
  - Missing '# description:' comment
```

### Manual Upgrade Process

1. **Add config version header:**
   ```yaml
   # config_version: 2
   # description: Your service description
   # https://github.com/owner/repo
   ```

2. **Update variable naming:**
   ```yaml
   # Before (v1)
   container_name: myservice

   # After (v2)
   container_name: ${MYSERVICE_CONTAINER_NAME:-myservice}
   ```

3. **Add missing labels:**
   ```yaml
   labels:
     - joyride.host.name=${MYSERVICE_HOST_NAME:-myservice}.${HOST_DOMAIN}
     - traefik.enable=${MYSERVICE_TRAEFIK_ENABLED:-true}
     - com.centurylinklabs.watchtower.enable=${MYSERVICE_WATCHTOWER_ENABLED:-true}
     - autoheal=${MYSERVICE_AUTOHEAL_ENABLED:-true}
   ```

4. **Add env_file directive:**
   ```yaml
   services:
     myservice:
       env_file:
         - ./services-enabled/myservice.env
   ```

5. **Add healthcheck (if using autoheal):**
   ```yaml
   healthcheck:
     test: ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1']
     interval: 60s
     timeout: 10s
     retries: 3
     start_period: 30s
   ```

6. **Verify environment variables:**
   ```yaml
   environment:
     - PUID=${PUID:-1000}
     - PGID=${PGID:-1000}
     - TZ=${TZ}
   ```

7. **Add localtime mount:**
   ```yaml
   volumes:
     - /etc/localtime:/etc/localtime:ro
   ```

### Re-run Scaffold

After upgrading the YAML:

```bash
# Regenerate env.template
make create-scaffold-env SERVICE=myservice

# Rebuild scaffolding for enabled service
make scaffold-build myservice
```

### Verify Upgrade

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint myservice
```

Should show `Valid: True` with no version errors.

## Complete Example

Here's a complete walkthrough of creating a new service.

### Step 1: Create from Template

```bash
make create-service SERVICE=gitea
```

### Step 2: Edit the YAML

```yaml
# config_version: 2
# description: Self-hosted Git service with web interface
# https://github.com/go-gitea/gitea
# https://hub.docker.com/r/gitea/gitea

networks:
  traefik:
    external: true

services:
  gitea:
    image: gitea/gitea:${GITEA_DOCKER_TAG:-latest}
    env_file:
      - ./services-enabled/gitea.env
    container_name: ${GITEA_CONTAINER_NAME:-gitea}
    restart: ${GITEA_RESTART:-unless-stopped}
    networks:
      - traefik
    volumes:
      - ./etc/gitea:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    environment:
      - USER_UID=${PUID:-1000}
      - USER_GID=${PGID:-1000}
      - TZ=${TZ}
      - GITEA__database__DB_TYPE=sqlite3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - joyride.host.name=${GITEA_HOST_NAME:-git}.${HOST_DOMAIN}
      - traefik.enable=${GITEA_TRAEFIK_ENABLED:-true}
      - traefik.http.routers.gitea.entrypoints=websecure
      - traefik.http.routers.gitea.rule=Host(`${GITEA_HOST_NAME:-git}.${HOST_DOMAIN}`)
      - traefik.http.services.gitea.loadbalancer.server.port=3000
      - com.centurylinklabs.watchtower.enable=${GITEA_WATCHTOWER_ENABLED:-true}
      - autoheal=${GITEA_AUTOHEAL_ENABLED:-true}
```

### Step 3: Generate env.template

```bash
make create-scaffold-env SERVICE=gitea
```

Creates `services-scaffold/gitea/env.template`:

```bash
###############################################
# Gitea Configuration
#
# Generated from services-scaffold/gitea/env.template
# To regenerate: make scaffold-build gitea
###############################################

# Docker image settings
GITEA_DOCKER_TAG=${GITEA_DOCKER_TAG:-latest}

# Container settings
GITEA_CONTAINER_NAME=${GITEA_CONTAINER_NAME:-gitea}
GITEA_RESTART=${GITEA_RESTART:-unless-stopped}

# Network settings
GITEA_HOST_NAME=${GITEA_HOST_NAME:-git}

# Feature flags
GITEA_TRAEFIK_ENABLED=${GITEA_TRAEFIK_ENABLED:-true}
GITEA_WATCHTOWER_ENABLED=${GITEA_WATCHTOWER_ENABLED:-true}
GITEA_AUTOHEAL_ENABLED=${GITEA_AUTOHEAL_ENABLED:-true}
```

### Step 4: Lint the Service

```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint gitea
```

Output:
```
Linting: gitea
Valid: True
```

### Step 5: Enable and Start

```bash
make enable-service gitea
make start-service gitea
```

This:
1. Creates symlink in `services-enabled/`
2. Generates `services-enabled/gitea.env` from template
3. Creates `etc/gitea/` directory
4. Starts the container

### Step 6: Access the Service

Visit `https://git.yourdomain.com` (or your configured hostname).

## Best Practices

### Variable Naming

- **Consistent prefix:** `${SERVICENAME_PURPOSE:-default}`
- **Uppercase:** `GITEA_HOST_NAME` not `gitea_host_name`
- **Descriptive:** `GITEA_ADMIN_PASSWORD` not `GITEA_PASS`

### Defaults

- Provide sensible defaults in the YAML
- Use `:-default` syntax for optional variables
- Required secrets should have no default: `${GITEA_SECRET_KEY}`

### Documentation

- Add inline comments for complex configuration
- Reference upstream documentation in header comments
- Create `services-scaffold/myservice/MESSAGE.txt` for post-install instructions

### Volume Mounts

- Configuration: `./etc/myservice`
- Application data: `./media/myservice`
- Read-only system files: `/etc/localtime:/etc/localtime:ro`

### Resource Limits

Only add if the service is resource-heavy:
```yaml
mem_limit: 4g
cpus: 2
```

### Port Exposure

Don't expose ports unless required for external access:
```yaml
# Bad: Exposes port to host
ports:
  - "8080:8080"

# Good: Only accessible via Traefik
# (no ports directive)
```

## Troubleshooting

### Service Won't Start

```bash
make logs gitea
```

Check for:
- Missing environment variables
- Incorrect volume paths
- Port conflicts

### Traefik 404

Check:
1. `loadbalancer.server.port` matches container port
2. Service is in traefik network
3. `traefik.enable=true`
4. Router rule matches hostname

### Variables Not Substituted

Ensure:
1. Variable is in `services-enabled/gitea.env`
2. Makefile loads env file (`--env-file`)
3. Syntax is correct: `${VAR}` not `$VAR`

### Linting Failures

Run lint to identify issues:
```bash
docker run --rm -v $(pwd):/app onramp-sietch python /scripts/services.py lint gitea
```

Follow the error messages to fix.

## Next Steps

- Review [Scaffolding Documentation](scaffolding.md) for advanced scaffold features
- See [Commands Reference](commands.md) for all available commands
- Check [Environment Variables](env-vars.md) for configuration options
