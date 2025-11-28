## Backing up and restoring immich database.

Adapted from the [Official Documentation for Immich.](https://immich.app/docs/administration/backup-and-restore)

1. Back up existing database.
   
    `docker exec -t immich_database pg_dumpall -c -U postgres | gzip > "/path/to/backup/dump.sql.gz"`
2. If containers are running, take them down. I'd recommend just running `make down`, but you can also just manually stop and remove the containers.
3. Remove any existing volumes for immich. e.g. `sudo rm -rf etc/immich/*` if run from the `onramp` directory.
4. **Create** the immich containers but do not **start** them with the following command. Make sure you're in the `onramp` directory!
    * If you're not running the nfs override: `docker compose --env_file ./.env -f services-available/immich.yml create`
    * If you're running the nfs override: `docker compose --env_file ./.env -f services-available/immich.yml -f overrides-available/immich-nfs.yml create`
5. Run `docker ps -a` and verify that the immich containers are showing the *Created* status.
6. Run `docker start immich_database` to manually start the database container. Wait a few seconds for the database to become ready to accept connections.
7. Log into the container with `docker exec -it immich_database /bin/bash`.
8. Run these commands in order:
    * `psql -U postgres`
    * `DROP DATABASE immich;` <!-- drop the old database to make 100% sure that it's gone. The DB **needs** to be empty for the import to work.
    * `CREATE DATABASE immich;`
    * `\q`
    * `exit` <!-- should drop you out of the container entirely and put you back into your normal shell.
9. Import the database dump file.
    
    `gunzip < "/path/to/backup/dump.sql.gz" | docker exec -i immich_database psql -U postgres -d immich`
10. Examine the output for any errors. If not, you should be good to go. Bring the rest of the containers up by running
    `make`
