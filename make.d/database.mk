#########################################################
##
## mariadb commands
##
#########################################################

ifndef MARIADB_CONTAINER_NAME
MARIADB_CONTAINER_NAME=mariadb
endif

# enable this to be asked for password to when you connect to the database
#mysql-connect = @docker exec -it $(MARIADB_CONTAINER_NAME) mysql -p

# enable this to not be asked for password to when you connect to the database
mysql-connect = @docker exec -it $(MARIADB_CONTAINER_NAME) mysql -p$(MARIADB_ROOT_PASSWORD)

first_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 1)
second_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 2)

password := $(shell openssl rand -hex 16)

mariadb-console: ## connect to the mariadb console
	$(mysql-connect)

create-database: ## create a database with the name of the first argument passed 
	$(mysql-connect) -e 'CREATE DATABASE IF NOT EXISTS $(first_arg);'

show-databases: ## show all databases
	$(mysql-connect) -e 'show databases;'

create-db-user: ## create a database user with the name of the first argument passed and the password of the second argument passed
	$(mysql-connect) -e 'CREATE USER $(first_arg) IDENTIFIED BY "'$(second_arg)'";'

create-db-user-pw: ## create a database user with the name of the first argument passed and a random password
	@echo Here is your password : $(password) : Please put it in the .env file under the service name
	$(mysql-connect) -e 'CREATE USER IF NOT EXISTS $(first_arg) IDENTIFIED BY "'$(password)'";'

grant-db-perms: ## grant all privileges to a database user with the name of the first argument passed on the database with the name of the first argument passed
	$(mysql-connect) -e 'GRANT ALL PRIVILEGES ON '$(first_arg)'.* TO $(first_arg);'

remove-db-user: ## remove a database user with the name of the first argument passed
	$(mysql-connect) -e 'DROP USER $(first_arg);'

drop-database: ## drop a database with the name of the first argument passed
	$(mysql-connect) -e 'DROP DATABASE $(first_arg);'

create-user-with-db: create-db-user-pw create-database grant-db-perms ## create a database user with the name of the first argument passed and a random password and create a database with the name of the first argument passed and grant all privileges to the user on the database
