# Contributing to OnRamp

Thank you for your interest in contributing to OnRamp!

## Ways to Contribute

- Report bugs and request features via GitHub Issues
- Submit pull requests for bug fixes or new features
- Add new service definitions
- Improve documentation
- Help answer questions in Issues/Discussions

## Development Setup

1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test locally
5. Submit a pull request

## Adding a New Service

### 1. Create the Service File

```bash
make create-service myservice
```

This creates `services-available/myservice.yml` from the template.

### 2. Edit the Service Definition

Follow existing services as examples. Required elements:

```yaml
networks:
  traefik:
    external: true

# description: Brief description of the service
# https://service-homepage.com

services:
  myservice:
    image: myservice:${MYSERVICE_DOCKER_TAG:-latest}
    container_name: ${MYSERVICE_CONTAINER_NAME:-myservice}
    restart: ${MYSERVICE_RESTART:-unless-stopped}
    networks:
      - traefik
    volumes:
      - ./etc/myservice:/config
    environment:
      - PUID=${PUID:-1000}
      - PGID=${PGID:-1000}
      - TZ=${TZ}
    labels:
      - traefik.enable=${MYSERVICE_TRAEFIK_ENABLED:-true}
      - traefik.http.routers.myservice.entrypoints=websecure
      - traefik.http.routers.myservice.rule=Host(`${MYSERVICE_HOST_NAME:-myservice}.${HOST_DOMAIN}`)
      - traefik.http.services.myservice.loadbalancer.server.port=8080
```

### 3. Add Scaffolding (if needed)

If the service needs initial configuration files:

```bash
mkdir -p services-scaffold/myservice
```

Add templates or static files:
- `*.template` - Processed with envsubst
- `*.static` - Copied without modification

See [docs/scaffolding.md](docs/scaffolding.md) for details.

### 4. Test Your Service

```bash
make enable-service myservice
make start-service myservice
make logs-service myservice
```

### 5. Update Documentation

Run the service documentation generator:
```bash
make generate-service-md
```

## Code Style

### Makefile

- Use tabs for indentation (required by make)
- Add help comments with `## description`
- Use `$(MAKE)` instead of `make` for recursive calls
- Prefix internal targets with `-` to suppress errors when appropriate

### YAML

- 2 spaces for indentation
- Use environment variable substitution: `${VAR:-default}`
- Include description comment at top of service files

### Shell Scripts

- Use `#!/bin/bash` shebang
- Quote variables: `"$VAR"` not `$VAR`
- Use `set -e` for error handling

## Pull Request Guidelines

1. **One feature per PR** - Keep changes focused
2. **Test locally** - Verify the service works
3. **Update docs** - Add/update documentation as needed
4. **Descriptive commits** - Use clear commit messages
5. **No secrets** - Never commit API keys, passwords, etc.

## Commit Message Format

```
type: brief description

Longer explanation if needed.
```

Types:
- `feat`: New feature or service
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change that doesn't add features or fix bugs
- `chore`: Maintenance tasks

Examples:
```
feat: add nextcloud service

fix: resolve traefik routing for jellyfin

docs: update scaffolding guide with new conventions
```

## Questions?

Open a GitHub Issue or Discussion for help.
