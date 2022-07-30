[![Discord notification Action](https://github.com/ilude/traefik-setup-docker-compose/actions/workflows/alert-traefik-project.yml/badge.svg)](https://github.com/ilude/traefik-setup-docker-compose/actions/workflows/alert-traefik-project.yml)
#### A docker-compose setup of common services with traefik using cloudflare dns-01 for letsencrypt certificates

This repo assumes that you are running a debian linux disto like ubuntu, so a few of the scripted commands below may need to be adjusted if you are running using a different distro or package management. You will need to install docker on your linux host, you can do this by following the steps here:
[Docker Linux Installation steps](https://docs.docker.com/desktop/linux/install/#generic-installation-steps)

or using this bash script on ubuntu available [here](https://gist.github.com/ilude/52b775682ec6ea5cc31933f81cef49f6)

you'll need a personal domain that's setup with Cloudflare
and an API token created like so

![Cloudflare api token](https://cdn.discordapp.com/attachments/979867396800131104/985259853696102420/unknown.png "Cloudflare api token")


if you need to you can run the following to do the basic setup automagically

```
sudo apt install git make nano -y

sudo mkdir /apps
sudo chown -R $USER:$USER /apps
cd /apps
git clone https://github.com/traefikturkey/onramp.git onramp
cd onramp

make start-staging
```

edit the .env file to include cloudflare credenitals your domain and the hostname of the current machine save the file by typing ctrl-x followed by the letter  traefik will start and attempt to obtain a staging certificate wait and then follow the on screen directions

```
make down-staging
```
you are now ready to bring things up with the production certificates

```
make
```

## Docker Services

other docker services are included in the ./services-available directory
The configuration files include links to the web page for the services which has 
the available documentation

to list them:
```
make list-services
```

they can be enabled by running the following commands:

```
make enable-service uptime-kuma
make restart
```

and disabled with the following:
```
make disable-service uptime-kuma
make restart
```

> Note: this creates a symlink file in ./services-enabled to the service.yml file in ./services-available

## Docker Overrides

Several docker overrides are included that allow extending the functionallity of existing services to add features like NFS mounted media directories and Intel Quicksync or Nvidia GPU support to the Plex and Jellyfin containers

to list avaliable overrides:
```
make list-overrides
```

to enable an override:
```
make enable-override plex-nfs
make restart
```

to disable and override:
```
make disable-override plex-nfs
make restart
```
> Note: this creates a symlink file in ./overrides-enabled to the override.yml file in ./overrides-available
> In addition users can place there own custom docker compose files into ./overrides-enabled and they will be included on normal start up 
> as well as included in the backup file created when running make create-backup
> for more info on docker compose overrides see: https://docs.docker.com/compose/extends/#adding-and-overriding-configuration

## Docker Game servers

Docker based Game servers are included in the ./services-available/games directory 
The configuration files include links to the web page for the services which has 
the available documentation

to list available games:
```
make list-games
```

to enable a game:
```
make enable-games factorio
make restart
```

and disabled a game:
```
make disable-games factorio
make restart
```

## External Services
External services can also be proxied through traefik to list the available configurations:

```
make list-external
```

they can be enabled by running the following commands:

```
make enable-external proxmox
make restart
```

and disabled with the following:
```
make disable-external proxmox
make restart
```
## Backing up Configuration

### create backup file
```
make create-backup
```
this will create a traefik-config-backup.tar.gz in the project directory

### copy backup file to another machine
```
scp ./backups/traefik-config-backup.tar.gz <user>@<other_host>:/apps/onramp/backups/
```

### restore backup file on the other machine
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

# you can run multiple commands at once like this
make; make logs
```
## Environment Variables

Many parts of the available services, overrides and games can be customized using variables set in your .env file
If you open an available file and view it you will likely see many variables such as ${UNIFI_DOCKER_TAG:-latest-ubuntu}

UNIFI_DOCKER_TAG is the variable name 
latest-ubuntu is the default value

You can override this value by placing the following line in your .env file
```
UNIFI_DOCKER_TAG=latest-ubuntu-beta
```
this will enable pulling the latest-ubuntu-beta version of the unifi container instead of the default stable version

Please see https://docs.docker.com/compose/environment-variables/ for more information about environment variable in docker compose
