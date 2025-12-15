# MediaManager Scaffold

## Overview

This scaffold generates the `config.toml` configuration file for MediaManager with proper PostgreSQL database credentials from the shared OnRamp postgres service.

## Files

- `config.toml.template` - Configuration template with environment variable substitution

## Configuration

The scaffold automatically configures:

1. **Database Connection**: Uses shared postgres service with credentials from `.env`
   - Host: `postgres`
   - Port: `5432`
   - User: From `PG_USER` (default: admin)
   - Password: From `PG_PASS`
   - Database: `mediamanager` (auto-created by scaffold)

2. **Frontend URL**: Configured from `HOST_DOMAIN` environment variable

3. **Token Secret**: Uses `MEDIAMANAGER_TOKEN_SECRET` if set, otherwise needs manual generation

## Usage

```bash
# Enable and scaffold the service
make enable-service mediamanager

# If config already exists and needs regeneration:
rm /apps/onramp/etc/mediamanager/config/config.toml
make scaffold-build mediamanager

# Start the service
make start-service mediamanager
```

## Notes

- MediaManager copies an example config on first boot if no config exists
- The scaffold template should be present before first container start
- If the container creates its own config, you'll need to manually update the database credentials
- Media directories (/data/images, /data/tv, /data/movies, /data/torrents) need to be mounted as volumes

## Environment Variables

Optional environment variables that can be set in `services-enabled/.env`:

- `MEDIAMANAGER_HOST_NAME` - Subdomain for the service (default: mediamanager)
- `MEDIAMANAGER_TOKEN_SECRET` - JWT token secret (auto-generated if not set)
- `MEDIAMANAGER_ADMIN_EMAIL` - Admin email address (default: admin@example.com)
