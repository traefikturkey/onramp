#### A docker-compose setup of common services with traefik using cloudflare dns-01 for letsencrypt certificates

This repo assumes that you are running a debian linux disto like ubuntu, so a few of the scripted commands below may need to be adjusted if you are running using a different distro or package management. You will need to install docker on your linux host, you can do this by following the steps here:
[Docker Linux Installation steps](https://docs.docker.com/desktop/linux/install/#generic-installation-steps)

or using this bash script on ubuntu available [here](https://gist.github.com/ilude/52b775682ec6ea5cc31933f81cef49f6)

you'll need a personal domain that's setup with Cloudflare
and an API token created like so

![Cloudflare api token](https://cdn.discordapp.com/attachments/979867396800131104/985259853696102420/unknown.png "Cloudflare api token")


if you need to you can run the following to do the basic setup automagically

```
sudo apt install git make -y

sudo mkdir /apps
sudo chown -R $USER:$USER /apps
git clone https://github.com/ilude/traefik-setup-docker-compose.git traefik-setup
cd /apps/traefik-setup

make start-staging

# edit the .env file to include cloudflare credenitals
# your domain and the hostname of the current machine
# save the file by typing ctrl-x followed by the letter y
# traefik will start and attempt to obtain a staging certificate
# wait and then follow the on screen directions

make down-staging

# you are now ready to bring things up with the production certificates

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
make enable-service samba
make restart
```

and disabled with the following:
```
make disable-service samba
make restart
```

## Docker Game servers

Docker based Game servers are included in the ./services-available/games directory 
The configuration files include links to the web page for the services which has 
the available documentation

to list them:
```
make list-games
```

they can be enabled by running the following commands:

```
make enable-games samba
make restart
```

and disabled with the following:
```
make disable-games samba
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
make export-backup
```
this will create a traefik-config-backup.tar.gz in the project directory

### copy backup file to another machine
```
scp traefik-config-backup.tar.gz <user>@<other_host>:/apps/traefik-setup
```

### restore backup file on the other machine
```
make import-backup
```

## Other make commands

Then you can run any of the following:

```
make          # does a docker compose up -d
make up       # does a docker compose up
make down     # does a docker compose down
make restart  # does a docker compose down followed by an up -d
make logs     # does a docker compose logs -f
make update   # does a docker compose down, pull (to get the latest docker images) and up -d

# you can run multiple commands at once like this
make; make logs
```
