#########################################################
##
## build related commands
##
#########################################################

ifneq (,$(wildcard ./services-enabled/authelia.yml))
	BUILD_DEPENDENCIES += etc/authelia/configuration.yml
endif

etc/authelia/configuration.yml:
	mkdir -p ./etc/authelia
	envsubst '$${HOST_DOMAIN}' < .templates/authelia_configuration.template > ./etc/authelia/configuration.yml

ifneq (,$(wildcard ./services-enabled/adguard.yml))
	BUILD_DEPENDENCIES += etc/adguard/conf/AdGuardHome.yaml
endif

etc/adguard/conf/AdGuardHome.yaml:
	mkdir -p ./etc/adguard/conf
	envsubst '$${ADGUARD_PASSWORD}, $${ADGUARD_USER}, $${HOST_DOMAIN}' < .templates/adguardhome.template > ./etc/adguard/conf/AdGuardHome.yaml

ifneq (,$(wildcard ./services-enabled/searnxg.yml))
	BUILD_DEPENDENCIES += etc/searnxg/settings.yaml
endif

etc/searnxg/settings.yaml:
	mkdir -p ./etc/searnxg
	envsubst < .templates/searxng.settings.template.yml > ./etc/searnxg/settings.yml

ifneq (,$(wildcard ./services-enabled/pihole.yml))
	BUILD_DEPENDENCIES += etc/pihole/dnsmasq/03-custom-dns-names.conf
endif

etc/pihole/dnsmasq/03-custom-dns-names.conf:
	envsubst '$${HOST_DOMAIN}, $${HOSTIP} ' < .templates/pihole_joyride.template > ./etc/pihole/dnsmasq/03-custom-dns-names.conf

ifneq (,$(wildcard ./services-enabled/dashy.yml))
	BUILD_DEPENDENCIES += etc/dashy/dashy-config.yml
endif

etc/dashy/dashy-config.yml:
	mkdir -p ./etc/dashy
	touch ./etc/dashy/dashy-config.yml

ifneq (,$(wildcard ./services-enabled/prometheus.yml))
	BUILD_DEPENDENCIES += etc/prometheus/conf
endif

etc/prometheus/conf:
	mkdir -p etc/prometheus/conf
	cp --no-clobber --recursive	.templates/prometheus-conf/* etc/prometheus/conf

ifneq (,$(wildcard ./services-enabled/recyclarr.yml))
	BUILD_DEPENDENCIES += etc/recyclarr/recyclarr.yml
endif

etc/recyclarr/recyclarr.yml:
	cp --no-clobber .templates/recyclarr.template .etc/recyclarr/recyclarr.yml


ifneq (,$(wildcard ./services-enabled/gatus.yml))
	BUILD_DEPENDENCIES += etc/gatus/config.yaml
endif

etc/gatus/config.yaml:
	cp --no-clobber .templates/gatus.template .etc/gatus/config.yaml

ifneq (,$(wildcard ./services-enabled/olivetin.yml))
	BUILD_DEPENDENCIES += etc/olivetin/config.yaml
endif

etc/olivetin/config.yaml:
	touch $@
