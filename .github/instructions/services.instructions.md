---
description: "Checklist for creating or updating service definitions"
applyTo: "services-available/**/*.yml"
---
# Authoring service files in `services-available`

- Scaffold new services with `make create-service <service-name>` to ensure the file includes the necessary structure and comments.
- Populate the comment header: keep `# description:` to a single sentence and add at least one upstream link (`# https://...`) for the automation that refreshes `SERVICES.md`.
- Parameterize image tags, container names, memory limits, Traefik hostnames, and other tunables with `${SERVICE_NAME_*}` environment variables so users can override them in `.env`.
- Mount configuration into `./etc/<service-name>` (or a subdirectory) whenever the container writes state; rely on the enable-service hook to create those paths instead of hardcoding host-specific locations.
- Keep Traefik labels aligned with existing conventions (`websecure` entrypoint, `traefik.docker.network=traefik`, Joyride host label, Watchtower and Autoheal flags). Only expose additional ports or middlewares when the service requires them.
- Confirm the container listens on the port referenced in the Traefik labels; override the command/entrypoint (for example, switch an MCP server to HTTP transport) when the upstream image defaults to a non-networked mode.
- Avoid embedding secrets or defaults that reveal credentials; reference environment variables instead and document any required keys in code comments or supporting docs.
- When the service needs seed files, place templates under `templates/services/<service-name>/` so the enable script can copy them on first run.
- Validate the YAML (`yamllint services-available/<service-name>.yml`) and, if possible, smoke-test with `make enable-service <service-name>` followed by `make start-service <service-name>` to ensure the container starts cleanly.
- Coordinate any global guardrail updates (for example, instructions in `.github/copilot-instructions.md`) in the corresponding documentation or pull request notes so teammates understand why the service definition changed.
