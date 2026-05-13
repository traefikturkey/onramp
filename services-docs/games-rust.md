# Games Rust

> Rust is a multiplayer-only survival video game

## Links
- [Official Documentation](https://richardpricejones.medium.com/how-to-create-your-own-rust-server-c37c49d22919)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/rust.yml)

## Docker Images
- `didstopia/rust-server`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `RUST_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `28015:28015`
- `28015:28015/udp`
- `28016:28016`
- `8080:8080`

### Volumes
- `./etc/games/rust:/steamcmd/rust` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.rust.entrypoints=websecure`
- `traefik.http.routers.rust.rule=Host(`rust.${HOST_DOMAIN}`)`
- `traefik.http.services.rust.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${RUST_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=rust.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-rust

# Configure environment variables (if needed)
make scaffold games-rust

# Start the service
make up
```
