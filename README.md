#### A docker-compose setup of common services with traefik using cloudflare dns-01 for letsencrypt certificates

if you haven't already install docker, you can use the script [here](https://gist.github.com/ilude/52b775682ec6ea5cc31933f81cef49f6)

you'll need a personal domain that's setup with Cloudflare
and an API token created like so

![Cloudflare api token](https://cdn.discordapp.com/attachments/979867396800131104/985259853696102420/unknown.png "Cloudflare api token")


if you need to you can run the following to do the basic setup automagically

```
sudo apt install git unzip -y

sudo mkdir /apps
sudo chown -R $USER:$USER /apps
git clone https://github.com/ilude/traefik-setup-docker-compose.git traefik-setup
cd traefik-setup
cp .env.sample .env

nano .env

# edit the .env file to include cloudflare credenitals
# your domain and the hostname of the current machine

make start-staging

# follow the on screen directions
# if everything worked then proceed

make down-staging

# you are now ready to bring things up with the production certificates

make

```

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

other services are included in the services directory, they can be copied down into the
main project directory and then things can be restarted using the command:

```
 make restart
```
