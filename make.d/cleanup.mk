#########################################################
#
# clean up commands
#
#########################################################

clean-acme:
	@echo "removing acme certificate file"
	-sudo rm etc/traefik/letsencrypt/acme.json

prune:
	docker image prune

prune-force:
	docker image prune -f

prune-update: prune-force update

remove-etc: 
	rm -rf ./etc/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/

reset-database-folder:
	rm -rf ./media/databases/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/
	git checkout ./media/databases/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/.keep

reset-etc: remove-etc
	git checkout ./etc/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/

stop-reset-etc: stop-service reset-etc

disable-remove-etc: disable-service remove-etc

disable-reset-etc: disable-service reset-etc

reset-database: remove-etc reset-database-folder	