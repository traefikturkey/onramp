#########################################################
##
## override commands
##
#########################################################

enable-override: overrides-enabled/$(SERVICE_PASSED_DNCASED).yml
overrides-enabled/$(SERVICE_PASSED_DNCASED).yml:
	@ln -s ../overrides-available/$(SERVICE_PASSED_DNCASED).yml ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml || true

remove-override: disable-override ## disble the override before removing it
disable-override:
	rm -f ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml