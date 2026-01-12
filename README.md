
#### A docker-compose setup of [common services](SERVICES.md) with Traefik using Cloudflare dns-01 for letsencrypt certificates

Here is a complete list of [available services](SERVICES.md) and [available games](SERVICES.md#available-games)

For detailed documentation, see the [docs/](docs/) folder:
- [Dashboard Guide](docs/dashboard.md) - Web UI for managing your homelab
- [Scaffolding Guide](docs/scaffolding.md) - Convention-based service configuration
- [Migration Guide](docs/main-branch-announcement.md) - Switching from master to main

Architecture documentation in [.github/shared/](.github/shared/):
- [Database Architecture](.github/shared/database-architecture.md) - Dedicated vs shared databases
- [Network Architecture](.github/shared/network-architecture.md) - Traefik and network patterns
- [Backup Strategy](.github/shared/backup-strategy.md) - Backup and restore procedures
- [Health Check Patterns](.github/shared/healthcheck-patterns.md) - Standard health checks

Onramp uses Docker and it installs docker if you don't alerady have it installed (a check is run as part of the 'make install' command below).

This repo assumes that you are running a debian linux disto like Ubuntu!

A podman version is available as a branch here: [https://github.com/traefikturkey/onramp/tree/podman](https://github.com/traefikturkey/onramp/tree/podman)
This branch is in testing and may have bugs/issues that are not present in main branch
Testing and PR's are welcome and encouraged!

You'll need a personal domain that's setup with Cloudflare
and an scoped API token created like shown below, [https://dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens) 

![Cloudflare api token](https://raw.githubusercontent.com/traefikturkey/onramp/master/documentation/assets/read%2Bedit-token.png "Cloudflare api token")


## Download OnRamp

After getting your Cloudflare API key
you can run the following to do the basic setup automagically:

```bash
sudo apt update
sudo apt install git make -y

sudo mkdir /apps
sudo chown -R $USER:$USER /apps
cd /apps
git clone https://github.com/traefikturkey/onramp.git onramp
cd onramp

make install
```

> **Note:** If this is a fresh system without Docker, `make install` will automatically install Docker and add your user to the docker group. After installation completes, you'll need to run `newgrp docker` (or log out and back in) to use Docker commands, then run `make install` again to complete setup.

Edit the environment file (`services-enabled/.env`) to include Cloudflare credentials, your domain and the hostname of the current machine, save the file and exit.

```bash
make edit-env-onramp
```

Then start the staging environment:

```bash
make start-staging
```

Traefik will start and attempt to obtain a staging certificate, wait and then follow the on screen directions.

```bash
make down-staging
```

You are now ready to bring things up with the production certificates

```bash
make
```

## Docker Services

Other docker services are included in the ./services-available directory.
The configuration files include links to the web page for the services which has 
the available documentation.

> Note : This also includes cautions and notices for some of the different services, so be sure to look at them.

To list them:
```
make list-services
```

They can be enabled by running the following commands:

```
make enable-service uptime-kuma
make restart
```
> Note: This creates a symlink file in `./services-enabled` to the service.yml file in `./services-available`.
> A `.env` file is always generated at `services-enabled/<service>.env` (from template if available, or auto-generated).
> Each service YAML has an `env_file:` directive pointing to this file.

and disabled with the following:
```
make disable-service uptime-kuma
make restart
```

To create a new service:
```
make create-service name-of-service
```

This will create a file in /services-available that is built using the make.d/templates/service.template



## Docker Overrides

Several docker overrides are included that allow extending the functionallity of existing services to add features like NFS mounted media directories and Intel Quicksync or Nvidia GPU support to the Plex and Jellyfin containers.

To list avaliable overrides:
```
make list-overrides
```

To enable an override:
```
make enable-override plex-nfs
make restart
```

To disable an override:
```
make disable-override plex-nfs
make restart
```
> Note: this creates a symlink file in ./overrides-enabled to the override.yml file in ./overrides-available
> In addition users can place there own custom docker compose files into ./overrides-enabled and they will be included on normal start up 
> as well as included in the backup file created when running make create-backup
> for more info on docker compose overrides see: https://docs.docker.com/compose/extends/#adding-and-overriding-configuration

## Docker Game servers

Docker based Game servers are included in the ./services-available/games directory.
The configuration files include links to the web page for the services which has 
the available documentation.

To list available games:
```
make list-games
```

To enable a game:
```
make enable-game factorio
make restart
```

To disable a game:
```
make disable-game factorio
make restart
```

## External Services
External services can also be proxied through Traefik to list the available configurations:

```
make list-external
```

They can be enabled by running the following commands:

```
make enable-external proxmox
make restart
```

And disabled with the following:
```
make disable-external proxmox
make restart
```

## Scaffolding

OnRamp uses convention-based scaffolding to auto-generate service configurations. When you enable a service that has templates in `services-scaffold/`, configs are automatically created in `etc/<service>/`.

See [docs/scaffolding.md](docs/scaffolding.md) for details on:
- How to add scaffolding to a service
- Template file conventions
- The difference between `disable-service` and `nuke-service`

## Backing up Configuration

### Disaster Recovery Philosophy
Instead of complex High Availability (HA) setups (like Docker Swarm or Kubernetes) which can be overkill for a home lab, OnRamp encourages a "Disaster Recovery" (DR) approach. The goal is to be able to rebuild your entire stack from scratch in minutes using backups and automation.

**The 3-2-1 Backup Strategy:**
- **3** copies of your data
- **2** different media types
- **1** offsite copy

By backing up your configuration and using tools like Ansible to provision the base OS, you can restore your services quickly on new hardware if a failure occurs.

### Create backup file
```
make create-backup
```
This will create `onramp-config-backup-{hostname}-{timestamp}.tar.gz` in the `backups/` directory

### Copy backup file to another machine
```
scp ./backups/onramp-config-backup-*.tar.gz <user>@<other_host>:/apps/onramp/backups/
```

### Restore backup file on the other machine
```
make restore-backup
```

## Other make commands

Then you can run any of the following:

```
make          # does a docker compose up -d
make up       # does a docker compose up (this will show you the log output of the containers, but will not stay running if you hit ctrl-c or log out)
make down     # does a docker compose down
make restart  # does a docker compose down followed by an up -d
make logs     # does a docker compose logs -f
make update   # does a docker compose down, pull (to get the latest docker images) and up -d

# You can run multiple commands at once like this
make; make logs
```
## Environment Variables

OnRamp uses a modular environment system where configuration is split into separate files:

- **Global config:** `services-enabled/.env` - Core settings (domain, Cloudflare credentials, timezone, etc.)
- **Service-specific:** `services-enabled/<service>.env` - Settings for individual services
- **NFS config:** `services-enabled/.env.nfs` - NFS mount settings (optional)
- **External services:** `services-enabled/.env.external` - External service proxy settings (optional)

### Editing Environment Files

```bash
make edit-env-onramp      # Edit global configuration
make edit-env <service>   # Edit service-specific config (e.g., make edit-env adguard)
make edit-env-nfs         # Edit NFS configuration
make edit-env-external    # Edit external services config
```

### Variable Syntax

If you open a service file, you'll see variables like `${UNIFI_DOCKER_TAG:-latest-ubuntu}`:
- `UNIFI_DOCKER_TAG` is the variable name
- `latest-ubuntu` is the default value

Override by adding to the appropriate env file:
```
UNIFI_DOCKER_TAG=latest-ubuntu-beta
```

### Migrating from Legacy .env

If you have an existing OnRamp installation with a monolithic `.env` file, the migration happens automatically on the first `make` command. Your old `.env` will be:
1. Split into appropriate `services-enabled/*.env` files
2. Backed up to `backups/.env.legacy`
3. Removed

To preview what migration would do:
```bash
make migrate-env-dry-run
```

Please see https://docs.docker.com/compose/environment-variables/ for more information about environment variables in docker compose

![Alt](https://repobeats.axiom.co/api/embed/1f05fd9a7be98c1958a107a05bd450049b2e9eb7.svg "Repobeats analytics image")
