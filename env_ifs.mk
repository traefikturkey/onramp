ifndef NETBOX_EMAIL
	NETBOX_SUPERUSER_EMAIL=$(CF_API_EMAIL)
endif

check-cf:
	@if [ "$(CF_API_EMAIL)" != "" ]; then echo "PASSED"; else echo "FAILED"; fi
	@if [ "$(CF_DNS_API_TOKEN)" != "" ]; then echo "PASSED"; else echo "FAILED"; fi
	@if [ "$(HOST_NAME)" != "" ]; then echo "PASSED"; else echo "FAILED"; fi
	@if [ "$(HOST_DOMAIN)" != "" ]; then echo "PASSED"; else echo "FAILED"; fi
	
check-authentik:	
	@if [ "$(AUTHENTIK_SECRET_KEY)" != "" ]; then echo "Secret key : PASSED"; else echo "FAILED : Please set your AUTHENTIK_SECRET_KEY in the .env file"; fi
	@if [ "$(PG_PASS_AUTHENTIK)" != "" ]; then echo "PASSED"; else echo "FAILED : Please set your PG_PASS_AUTHENTIK in the .env file"; fi
	@if [ "$(AUTHENTIK_BOOTSTRAP_PASSWORD)" != "" ]; then echo "PASSED"; else echo "FAILED : Please set your AUTHENTIK_BOOTSTRAP_PASSWORD in the .env file"; fi

check-authelia:
	@if [ "$(AUTHELIA_JWT_SECRET)" != "" ]; then echo "PASSED"; else echo "FAILED"; fi
