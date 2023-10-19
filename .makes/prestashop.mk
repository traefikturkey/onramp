#########################################################
#
# prestashop commands
#
#########################################################

remove-presta-install-folder:
	@sudo rm -rf etc/prestashop/install/

rename-presta-admin:
	@sudo mv etc/prestashop/admin/ etc/prestashop/$(first_arg)
