#########################################################
## 
## scaffolding commands 
##
#########################################################

create-service-scaffold: ## Creates the directory and file structure for a service within the services-scaffold directory.
	mkdir -p ./services-scaffold/$(SERVICE_PASSED_DNCASED)
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/scaffold-build-up.template > services-scaffold/$(SERVICE_PASSED_DNCASED)/build-up.sh
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/scaffold-tear-down.template > services-scaffold/$(SERVICE_PASSED_DNCASED)/tear-down.sh
	sudo chmod +x services-scaffold/$(SERVICE_PASSED_DNCASED)/*.sh

remove-service-scaffold: ## Removes the service directory from within the services-scaffold directory.
	sudo rm -rf ./services-scaffold/$(SERVICE_PASSED_DNCASED)

scaffold-build-up:  ## Executes the build-up script for the passed service.
	bash ./services-scaffold/$(SERVICE_PASSED_DNCASED)/build-up.sh

scaffold-tear-down: ##  Executes the tear-down script for the passed service.
	bash ./services-scaffold/$(SERVICE_PASSED_DNCASED)/tear-down.sh

list-scaffolds: ## list available scaffolds
	@find ./services-scaffold/* -type d | cut -d"/" -f3 | sort -u