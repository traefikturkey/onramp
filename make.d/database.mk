#########################################################
#
# mariadb commands
#
#########################################################

ifndef MARIADB_CONTAINER_NAME
MARIADB_CONTAINER_NAME=mariadb
endif

# enable this to be asked for password to when you connect to the database
# mysql-connect = @docker exec -it $(MARIADB_CONTAINER_NAME) mysql -p
# Broken ^^

mysql-connect = @docker exec -it $(MARIADB_CONTAINER_NAME) $(MARIADB_CONTAINER_NAME) -p

first_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 1)
second_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 2)

password := $(shell openssl rand -hex 16)

mariadb-console:
	$(mysql-connect)

create-database:
	$(mysql-connect) -e 'CREATE DATABASE IF NOT EXISTS $(first_arg);'

show-databases: 
	$(mysql-connect) -e 'show databases;'

create-db-user:
	$(mysql-connect) -e 'CREATE USER $(first_arg) IDENTIFIED BY "'$(second_arg)'";'

create-db-user-pw: 
	@echo Here is your password : $(password) : Please put it in the .env file under the service name
	$(mysql-connect) -e 'CREATE USER IF NOT EXISTS $(first_arg) IDENTIFIED BY "'$(password)'";'

grant-db-perms:
	$(mysql-connect) -e 'GRANT ALL PRIVILEGES ON '$(first_arg)'.* TO $(first_arg);'

remove-db-user: 
	$(mysql-connect) -e 'DROP USER $(first_arg);'

drop-database:
	$(mysql-connect) -e 'DROP DATABASE $(first_arg);'

create-user-with-db: create-db-user-pw create-database grant-db-perms
