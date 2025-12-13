#########################################################
##
## MariaDB Database Operations
##
#########################################################

.PHONY: mariadb-console mariadb-list-databases mariadb-create-db mariadb-drop-db

mariadb-console: sietch-build ## Open interactive MariaDB console
	$(SIETCH_RUN) python /scripts/mariadb_manager.py console

mariadb-list-databases: sietch-build ## List all MariaDB databases
	$(SIETCH_RUN) python /scripts/mariadb_manager.py list-databases

mariadb-create-db: sietch-build ## Create a MariaDB database (usage: make mariadb-create-db dbname)
	$(SIETCH_RUN) python /scripts/mariadb_manager.py create-db $(first_arg)

mariadb-drop-db: sietch-build ## Drop a MariaDB database (usage: make mariadb-drop-db dbname)
	$(SIETCH_RUN) python /scripts/mariadb_manager.py drop-db $(first_arg)

mariadb-database-exists: sietch-build ## Check if a MariaDB database exists (usage: make mariadb-database-exists dbname)
	$(SIETCH_RUN) python /scripts/mariadb_manager.py database-exists $(first_arg)

mariadb-backup-db: sietch-build ## Backup a MariaDB database (usage: make mariadb-backup-db dbname output.sql)
	$(SIETCH_RUN) python /scripts/mariadb_manager.py backup-db $(first_arg) $(second_arg)

# Legacy target mappings for backwards compatibility
show-databases: mariadb-list-databases ## DEPRECATED: Use mariadb-list-databases
create-database: mariadb-create-db ## DEPRECATED: Use mariadb-create-db
drop-database: mariadb-drop-db ## DEPRECATED: Use mariadb-drop-db

# Variable setup (must come after first_arg/second_arg usage)
first_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 1)
second_arg = $(shell echo $(EMPTY_TARGETS)| cut -d ' ' -f 2)
