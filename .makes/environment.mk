#########################################################
#
# environment helper commands
#
#########################################################

create-environment-template:
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/environment.template > environments-available/$(SERVICE_PASSED_DNCASED).template
	$(EDITOR) environments-available/$(SERVICE_PASSED_DNCASED).template

edit-env-template:
	$(EDITOR) environments-available/$(SERVICE_PASSED_DNCASED).template

edit-env:
	$(EDITOR) environments-enabled/$(SERVICE_PASSED_DNCASED).env

edit-env-onramp:
	$(EDITOR) environments-enabled/onramp.env

edit-env-nfs:
	$(EDITOR) environments-enabled/onramp-nfs.env

edit-env-external:
	$(EDITOR) environments-enabled/onramp-external.env

regenerate-env:
	@python3 scripts/env-subst.py environments-available/$(SERVICE_PASSED_DNCASED).template $(SERVICE_PASSED_UPCASED)

show-env:
	@env | sort