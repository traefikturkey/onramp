# OnRamp Services Documentation

This directory contains comprehensive documentation for all 276+ OnRamp services.

## Documentation Structure

Each service has its own markdown file with the following sections:

### Service Overview
- **Title**: Service name
- **Description**: Brief description of what the service does
- **Links**: Official repository, Docker Hub, documentation, and configuration files

### Docker Images
List of all Docker images used by the service

### Environment Variables
Complete table of environment variables with:
- Variable name
- Default value (from env.template if available)
- Description (inferred from variable name and context)

### Configuration

#### Ports
All exposed and internal ports used by the service

#### Volumes
Volume mounts for data persistence, configuration, and file storage

#### Networks
Docker networks the service connects to

#### Labels
Service labels organized by type:
- **Traefik Configuration**: Reverse proxy settings (routing rules, entrypoints, middlewares)
- **Watchtower Configuration**: Auto-update settings
- **Other Labels**: Joyride DNS, Autoheal, etc.

#### Dependencies
Other services that this service depends on

### Quick Start
Standard commands to enable, configure, and start the service:
```bash
make enable <service>
make scaffold <service>
make up
```

### Notes
Additional important information about multi-container services and dependencies

## How to Use

### Browse All Services
See [SERVICES.md](../SERVICES.md) for the complete alphabetical list of all available services.

### View Service Documentation
Click on any service name in SERVICES.md to view its full documentation.

### Enable a Service
1. Find the service you want in [SERVICES.md](../SERVICES.md)
2. Read its documentation to understand requirements
3. Run the Quick Start commands to enable and configure it

## Documentation Generation

This documentation is automatically generated from:
- Service YAML files in `services-available/`
- Environment templates in `services-scaffold/*/env.template`
- Metadata comments in YAML files

To regenerate all documentation:
```bash
cd sietch
uv run python scripts/generate_service_docs.py
```

To update SERVICES.md with new links:
```bash
cd sietch
uv run python scripts/update_services_md.py
```

## Service Categories

OnRamp includes services in these categories:

### Infrastructure & Monitoring
- DNS servers (AdGuard, Pi-hole, CoreDNS, Unbound)
- Monitoring (Uptime Kuma, Grafana, Prometheus, Beszel)
- Log viewers (Dozzle, Glances)
- Container management (Portainer, Yacht, Watchtower)

### Media & Entertainment
- Media servers (Plex, Jellyfin, Emby)
- Media management (*arr stack: Sonarr, Radarr, Lidarr, etc.)
- Music (Navidrome, Audiobookshelf)
- Photos (Immich, PhotoPrism, Lychee)

### Productivity & Documentation
- Note-taking (Joplin, Obsidian, Trilium)
- Wikis (Wiki.js, Docmost)
- Recipe management (Mealie, Tandoor)
- Task management (Vikunja, Super Productivity)

### Development & DevOps
- Git hosting (Gitea, Forgejo, GitLab)
- CI/CD (Drone CI, Woodpecker)
- Code editors (Code Server)
- Database management (pgAdmin, phpMyAdmin, CloudBeaver)

### Security & Access
- VPNs (WireGuard, Gluetun)
- Authentication (Authelia, Authentik)
- Password managers (Vaultwarden)
- Network security (CrowdSec)

### Home Automation & IoT
- Home automation platforms (Home Assistant via external integrations)
- MQTT brokers (Mosquitto)
- Camera systems (Frigate)

### AI & Machine Learning
- LLM servers (Ollama, Open WebUI)
- Image generation (Stable Diffusion, ComfyUI, Fooocus)
- Embedding servers (ChromaDB, Infinity)

### Communication & Social
- Chat servers (Matrix Synapse)
- Notification systems (Gotify, Ntfy, Apprise)

### File Storage & Sharing
- Cloud storage (Nextcloud)
- File sharing (PingVin Share, CopyParty)
- S3-compatible storage (MinIO, Garage)

### Web Applications
- Dashboards (Dashy, Homer, Homarr, Homepage)
- Bookmarking (Linkding)
- RSS readers (FreshRSS)
- URL shorteners (Shlink)

## Contributing

To add a new service:
1. Create the service YAML file in `services-available/`
2. Add metadata comments for description and documentation URL
3. Optionally create `services-scaffold/<service>/env.template`
4. Run the documentation generator
5. Update SERVICES.md

## Support

For issues or questions:
- Check the service's official documentation
- Review the service YAML configuration
- Visit the [OnRamp GitHub repository](https://github.com/traefikturkey/onramp)
