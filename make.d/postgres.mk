#########################################################
##
## PostgreSQL Database Operations
##
#########################################################

.PHONY: postgres-console postgres-list-databases postgres-create-db postgres-drop-db

postgres-console: ## Open interactive PostgreSQL console
	$(SIETCH_RUN) python /scripts/postgres_manager.py console

postgres-list-databases: ## List all PostgreSQL databases
	$(SIETCH_RUN) python /scripts/postgres_manager.py list-databases

postgres-create-db: ## Create a PostgreSQL database (usage: make postgres-create-db dbname)
	$(SIETCH_RUN) python /scripts/postgres_manager.py create-db $(first_arg)

postgres-drop-db: ## Drop a PostgreSQL database (usage: make postgres-drop-db dbname)
	$(SIETCH_RUN) python /scripts/postgres_manager.py drop-db $(first_arg)

postgres-database-exists: ## Check if a PostgreSQL database exists (usage: make postgres-database-exists dbname)
	$(SIETCH_RUN) python /scripts/postgres_manager.py database-exists $(first_arg)
