#########################################################
##
## clean up commands
##
#########################################################

clean-acme: ## remove acme certificate file (forces certificate renewal)
	@echo "This will delete your SSL certificates. Traefik will request new ones on next start."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || { echo "Cancelled."; exit 1; }
	@echo "removing acme certificate file"
	-sudo rm etc/traefik/letsencrypt/acme.json

prune: ## remove unused docker images
	docker image prune

prune-force: ## remove unused docker images with force
	docker image prune -a -f

prune-update: prune-force update ## remove unused docker images with force and update

remove-etc:  ## remove etc folder of a given service
	@echo "This will permanently delete ./etc/$(SERVICE_PASSED_DNCASED)/ and all its configuration."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || { echo "Cancelled."; exit 1; }
	rm -rf ./etc/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/

reset-database-folder: ## remove database folder of a given service
	@echo "This will permanently delete the database for $(SERVICE_PASSED_DNCASED). All data will be lost."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || { echo "Cancelled."; exit 1; }
	rm -rf ./media/databases/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/
	git checkout ./media/databases/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/.keep

reset-etc: remove-etc ## reset etc folder of a given service
	git checkout ./etc/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/

stop-reset-etc: stop-service reset-etc ## stop and reset etc folder of a given service

disable-remove-etc: disable-service remove-etc ## disable and remove etc folder of a given service

disable-reset-etc: disable-service reset-etc ## disable and reset etc folder of a given service

reset-database: remove-etc reset-database-folder ## reset database folder of a given database-service
