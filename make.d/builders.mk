#########################################################
##
## build related commands
##
#########################################################

ifneq (,$(wildcard ./services-enabled/authelia.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/authelia/configuration.yml)
endif

etc/authelia/configuration.yml:
	@mkdir -p ./etc/authelia
	@envsubst '$${HOST_DOMAIN}' < .templates/authelia_configuration.template > ./etc/authelia/configuration.yml

ifneq (,$(wildcard ./services-enabled/adguard.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/adguard/conf/AdGuardHome.yaml)
endif

etc/adguard/conf/AdGuardHome.yaml:
	@mkdir -p ./etc/adguard/conf
	@envsubst '$${ADGUARD_PASSWORD}, $${ADGUARD_USER}, $${HOST_DOMAIN}' < .templates/adguardhome.template > ./etc/adguard/conf/AdGuardHome.yaml

ifneq (,$(wildcard ./services-enabled/searnxg.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/searnxg/settings.yaml)
endif

etc/searnxg/settings.yaml:
	@mkdir -p ./etc/searnxg
	@envsubst < .templates/searxng.settings.template.yml > ./etc/searnxg/settings.yml

ifneq (,$(wildcard ./services-enabled/pihole.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/pihole/dnsmasq/03-custom-dns-names.conf)
endif

etc/pihole/dnsmasq/03-custom-dns-names.conf:
	@envsubst '$${HOST_DOMAIN}, $${HOSTIP} ' < .templates/pihole_joyride.template > ./etc/pihole/dnsmasq/03-custom-dns-names.conf

ifneq (,$(wildcard ./services-enabled/dashy.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/dashy/dashy-config.yml)
endif

etc/dashy/dashy-config.yml:
	@mkdir -p ./etc/dashy
	@touch ./etc/dashy/dashy-config.yml

ifneq (,$(wildcard ./services-enabled/prometheus.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/prometheus/conf)
endif

etc/prometheus/conf:
	@mkdir -p etc/prometheus/conf
	@cp --no-clobber --recursive	.templates/prometheus-conf/* etc/prometheus/conf

ifneq (,$(wildcard ./services-enabled/recyclarr.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/recyclarr/recyclarr.yml)
endif

etc/recyclarr/recyclarr.yml:
	@cp --no-clobber .templates/recyclarr.template .etc/recyclarr/recyclarr.yml


ifneq (,$(wildcard ./services-enabled/gatus.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/gatus/config.yaml)
endif

etc/gatus/config.yaml:
	@cp --no-clobber .templates/gatus.template .etc/gatus/config.yaml

ifneq (,$(wildcard ./services-enabled/olivetin.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/olivetin/config.yaml)
endif

etc/olivetin/config.yaml:
	@touch $@

ifneq (,$(wildcard ./services-enabled/cloudflare-tunnel.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),cloudflare-tunnel)
endif

ifneq (,$(wildcard ./services-enabled/onboard.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-onboard)
endif

setup-onboard:
	@mkdir -p ./etc/onboard/cache
	@mkdir -p ./etc/onboard/icons
	@sudo chown -R $(USER):$(USER) ./etc/onboard


ifneq (,$(wildcard ./services-enabled/omada.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-omada)
endif

setup-omada:
	@mkdir -p ./etc/omada/data
	@mkdir -p ./etc/omada/work
	@mkdir -p ./etc/omada/logs


ifneq (,$(wildcard ./services-enabled/audiobookshelf.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-audiobookshelf)
endif

setup-audiobookshelf:
	@mkdir -p ./etc/audiobookshelf/config
	@mkdir -p ./etc/audiobookshelf/metadata

ifneq (,$(wildcard ./services-enabled/uptime-kuma.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-uptime-kuma)
endif

setup-uptime-kuma:
	@mkdir -p ./etc/uptime-kuma

ifneq (,$(wildcard ./services-enabled/joyride.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-joyride)
endif

setup-joyride:
	@mkdir -p ./etc/joyride/hosts.d

ifneq (,$(wildcard ./override-enabled/wordpress-upload.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-wordpress-upload)
endif

setup-wordpress-upload:
	@mkdir -p ./etc/wordpress
	@cp --no-clobber .templates/wordpress-upload.template .etc/wordpress/upload.ini


ifneq (,$(wildcard ./etc/traefik/letsencrypt/acme.json))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),fix-acme-json-permissions)
endif

fix-acme-json-permissions:
	@sudo chmod 600 ./etc/traefik/letsencrypt/acme.json

#$(info "builders.mk loaded")