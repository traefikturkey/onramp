ifndef NETBOX_EMAIL
	NETBOX_SUPERUSER_EMAIL=$(CF_API_EMAIL)
endif

check-cf:
	@if [ "$(CF_API_EMAIL)" != "" ]; 		then echo "CF_API_EMAIL:		PASSED"; else echo "FAILED : Please set your CF_API_EMAIL in the onramp.env file"; fi
	@if [ "$(CF_DNS_API_TOKEN)" != "" ]; 	then echo "CF_DNS_API_TOKEN:	PASSED"; else echo "FAILED : Please set your CF_DNS_API_TOKEN in the onramp.env file"; fi
	@if [ "$(HOST_NAME)" != "" ]; 			then echo "HOST_NAME:			PASSED"; else echo "FAILED : Please set your HOST_NAME in the onramp.env file"; fi
	@if [ "$(HOST_DOMAIN)" != "" ]; 		then echo "HOST_DOMAIN:			PASSED"; else echo "FAILED : Please set your HOST_DOMAIN in the onramp.env file"; fi
	
check-authentik:	
	@if [ "$(AUTHENTIK_SECRET_KEY)" != "" ]; then echo "AUTHENTIK_SECRET_KEY : PASSED"; else echo "FAILED : Please set your AUTHENTIK_SECRET_KEY in the .env file"; fi
	@if [ "$(PG_PASS_AUTHENTIK)" != "" ]; then echo "PG_PASS_AUTHENTIK : PASSED"; else echo "FAILED : Please set your PG_PASS_AUTHENTIK in the .env file"; fi
	@if [ "$(AUTHENTIK_BOOTSTRAP_PASSWORD)" != "" ]; then echo "AUTHENTIK_BOOTSTRAP_PASSWORD: PASSED"; else echo "FAILED : Please set your AUTHENTIK_BOOTSTRAP_PASSWORD in the .env file"; fi

check-authelia:
	@if [ "$(AUTHELIA_JWT_SECRET)" != "" ]; then echo "AUTHELIA_JWT_SECRET : PASSED"; else echo "FAILED : Please set your AUTHENTIK_SECRET_KEY in the .env file"; fi
