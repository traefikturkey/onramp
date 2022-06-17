#### A docker-compose setup of common services with traefik using cloudflare dns-01 for letsencrypt certificates

if you haven't already install docker, you can use the script [here](https://gist.github.com/ilude/52b775682ec6ea5cc31933f81cef49f6)

you'll need a personal domain that's setup with Cloudflare
and an API token created like so

![Cloudflare api token](https://cdn.discordapp.com/attachments/979867396800131104/985259853696102420/unknown.png "Cloudflare api token")


if you need to you can run the following to do the basic setup automagically

```
sudo mkdir -p /apps/traefik
sudo chown -R $USER:$USER /apps
cd /apps/traefik
curl https://gist.githubusercontent.com/ilude/4814e69adc188020b964e8b45dd0a00f/raw/.env?$(date +%s) --output .env
curl https://gist.githubusercontent.com/ilude/4814e69adc188020b964e8b45dd0a00f/raw/Makefile?$(date +%s) --output Makefile
curl https://gist.githubusercontent.com/ilude/4814e69adc188020b964e8b45dd0a00f/raw/docker-compose.yml?$(date +%s) --output docker-compose.yml

nano .env
```

Then you can run any of the following:

```
make          # does a docker compose up -d
make up       # does a docker compose up
make down     # does a docker compose down
make restart  # does a docker compose down followed by an up -d
make logs     # does a docker compose logs -f
make update   # does a docker compose down, pull (to get the latest docker images) and up -d

# personally I like to run
make; make logs
```
 other services are included in the files below, they can be added to the /apps/traefik directory and will start up the next time you down and up again