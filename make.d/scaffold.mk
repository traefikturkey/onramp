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

scaffold-build-up:
	bash ./services-scaffold/$(SERVICE_PASSED_DNCASED)/build-up.sh

scaffold-tear-down:
	bash ./services-scaffold/$(SERVICE_PASSED_DNCASED)/tear-down.sh