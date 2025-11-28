#########################################################
##
## mariadb commands
##
#########################################################

ifndef MARIADB_CONTAINER_NAME
MARIADB_CONTAINER_NAME=mariadb
endif

first_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 1)
second_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 2)

mariadb-console: sietch-build ## connect to the mariadb console
	$(SIETCH_RUN) python /scripts/database.py console --container $(MARIADB_CONTAINER_NAME)

create-database: sietch-build ## create a database with the name of the first argument passed
	$(SIETCH_RUN) python /scripts/database.py create-db $(first_arg) --container $(MARIADB_CONTAINER_NAME)

show-databases: sietch-build ## show all databases
	$(SIETCH_RUN) python /scripts/database.py list-databases --container $(MARIADB_CONTAINER_NAME)

create-db-user: sietch-build ## create a database user with the name of the first argument and password of the second
	$(SIETCH_RUN) python /scripts/database.py create-user $(first_arg) --password $(second_arg) --container $(MARIADB_CONTAINER_NAME)

create-db-user-pw: sietch-build ## create a database user with generated password (saved to file)
	$(SIETCH_RUN) python /scripts/database.py create-user $(first_arg) --generate --container $(MARIADB_CONTAINER_NAME)

grant-db-perms: sietch-build ## grant all privileges on database to user (first arg = db/user name)
	$(SIETCH_RUN) python /scripts/database.py grant $(first_arg) $(first_arg) --container $(MARIADB_CONTAINER_NAME)

remove-db-user: sietch-build ## remove a database user
	$(SIETCH_RUN) python /scripts/database.py remove-user $(first_arg) --container $(MARIADB_CONTAINER_NAME)

drop-database: sietch-build ## drop a database
	$(SIETCH_RUN) python /scripts/database.py drop-db $(first_arg) --container $(MARIADB_CONTAINER_NAME)

create-user-with-db: sietch-build ## create user + database + grant (all-in-one)
	$(SIETCH_RUN) python /scripts/database.py setup $(first_arg) --container $(MARIADB_CONTAINER_NAME)
