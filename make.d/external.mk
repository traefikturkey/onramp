#########################################################
##
## external commands
##
#########################################################

disable-external: ## disable an external service
	rm ./etc/traefik/enabled/$(SERVICE_PASSED_DNCASED).yml

enable-external: ## enable an external service
	@cp  --no-clobber ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml ./etc/traefik/enabled/$(SERVICE_PASSED_DNCASED).yml || true

create-external: ## create an external service
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/external.template > ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml