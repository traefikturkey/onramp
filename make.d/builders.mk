#########################################################
##
## build related commands
##
#########################################################

ifneq (,$(wildcard ./services-enabled/authelia.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/authelia/configuration.yml)
endif

etc/authelia/configuration.yml:
	mkdir -p ./etc/authelia
	envsubst '$${HOST_DOMAIN}' < .templates/authelia_configuration.template > ./etc/authelia/configuration.yml

ifneq (,$(wildcard ./services-enabled/adguard.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/adguard/conf/AdGuardHome.yaml)
endif

etc/adguard/conf/AdGuardHome.yaml:
	mkdir -p ./etc/adguard/conf
	envsubst '$${ADGUARD_PASSWORD}, $${ADGUARD_USER}, $${HOST_DOMAIN}' < .templates/adguardhome.template > ./etc/adguard/conf/AdGuardHome.yaml

ifneq (,$(wildcard ./services-enabled/searnxg.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/searnxg/settings.yaml)
endif

etc/searnxg/settings.yaml:
	mkdir -p ./etc/searnxg
	envsubst < .templates/searxng.settings.template.yml > ./etc/searnxg/settings.yml

ifneq (,$(wildcard ./services-enabled/pihole.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/pihole/dnsmasq/03-custom-dns-names.conf)
endif

etc/pihole/dnsmasq/03-custom-dns-names.conf:
	envsubst '$${HOST_DOMAIN}, $${HOSTIP} ' < .templates/pihole_joyride.template > ./etc/pihole/dnsmasq/03-custom-dns-names.conf

ifneq (,$(wildcard ./services-enabled/joyride.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/joyride/hosts.d/hosts)
endif

etc/joyride/hosts.d/hosts:
	mkdir -p ./etc/joyride/hosts.d
	touch ./etc/joyride/hosts.d/hosts

ifneq (,$(wildcard ./services-enabled/pocketbase.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/pocketbase)
endif

etc/pocketbase:
	mkdir -p ./etc/pocketbase/data
	mkdir -p ./etc/pocketbase/public
	mkdir -p ./etc/pocketbase/hooks

ifneq (,$(wildcard ./services-enabled/copyparty.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/copyparty/config/copyparty.conf)
endif

etc/copyparty/config/copyparty.conf:
	mkdir -p ./etc/copyparty/config
	cp --no-clobber .templates/copyparty.conf etc/copyparty/config/copyparty.conf

ifneq (,$(wildcard ./services-enabled/dashy.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/dashy/dashy-config.yml)
endif

etc/dashy/dashy-config.yml:
	mkdir -p ./etc/dashy
	touch ./etc/dashy/dashy-config.yml

ifneq (,$(wildcard ./services-enabled/prometheus.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/prometheus/conf)
endif

etc/prometheus/conf:
	mkdir -p etc/prometheus/conf
	cp --no-clobber --recursive	.templates/prometheus-conf/* etc/prometheus/conf

ifneq (,$(wildcard ./services-enabled/recyclarr.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/recyclarr/recyclarr.yml)
endif

etc/recyclarr/recyclarr.yml:
	cp --no-clobber .templates/recyclarr.template ./etc/recyclarr/recyclarr.yml


ifneq (,$(wildcard ./services-enabled/gatus.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/gatus/config.yaml)
endif

etc/gatus/config.yaml:
	cp --no-clobber .templates/gatus.template ./etc/gatus/config.yaml

ifneq (,$(wildcard ./services-enabled/olivetin.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),etc/olivetin/config.yaml)
endif

etc/olivetin/config.yaml:
	touch $@

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

ifneq (,$(wildcard ./services-enabled/rundeck.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-rundeck)
endif

setup-rundeck:
	@mkdir -p ./etc/rundeck/db
	@mkdir -p ./etc/rundeck/config

ifneq (,$(wildcard ./override-enabled/wordpress-upload.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-wordpress-upload)
endif

setup-wordpress-upload:
	@mkdir -p ./etc/wordpress
	cp --no-clobber .templates/wordpress-upload.template ./etc/wordpress/upload.ini

ifneq (,$(wildcard ./services-enabled/tandoor.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-tandoor)
endif

setup-tandoor:
	@mkdir -p ./etc/tandoor/nginx
	envsubst '$${TANDOOR_HOST_NAME}, $${HOST_DOMAIN} '< ./.templates/recipes.conf.nginx.template > ./etc/tandoor/nginx/recipes.conf
	
ifneq (,$(wildcard ./services-enabled/docker-mirror.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),setup-docker-mirror)
endif

setup-docker-mirror:
	@mkdir -p ./etc/docker-mirror/registry
	@mkdir -p ./etc/docker-mirror/registry_data
	cp --no-clobber .templates/docker-mirror-config.template ./etc/docker-mirror/config.json

ifneq (,$(wildcard ./services-enabled/kaneo.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),build_kaneo_dirs)
endif

build_kaneo_dirs:
	mkdir -p ./etc/kaneo/db
	chown -R $USER:$USER ./etc/kaneo
	chmod g+s ./etc/kaneo

ifneq (,$(wildcard ./services-enabled/radarr.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),build_radarr_dirs)
endif

	if [ -z "$$(ls -A ./etc/radarr/custom-services.d 2>/dev/null)" ]; then \
		echo "custom-services.d is empty → downloading scripts_init.bash"; \
		wget -q -P ./etc/radarr/custom-cont-init.d \
			https://raw.githubusercontent.com/RandomNinjaAtk/arr-scripts/main/radarr/scripts_init.bash; \
	else \
		echo "custom-services.d has content → skipping download and cleaning old init script"; \
		if [ -f ./etc/radarr/custom-cont-init.d/scripts_init.bash ]; then \
			rm -f ./etc/radarr/custom-cont-init.d/scripts_init.bash; \
			echo "Removed ./etc/radarr/custom-cont-init.d/scripts_init.bash"; \
		fi; \
	fi

	if [ ! -f ./etc/radarr/extended.conf ]; then \
		echo "extended.conf not found → creating from template"; \
		cp ./templates/radarr_extended.template ./etc/radarr/extended.conf; \
	else \
		echo "extended.conf already exists → skipping creation"; \
	fi
	chown -R $USER:$USER ./etc/radarr
	chmod g+s ./etc/radarr

ifneq (,$(wildcard ./services-enabled/sonarr.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),build_sonarr_dirs)
endif

build_sonarr_dirs:
	@echo "Creating sonarr directories..."
	mkdir -p ./etc/sonarr/custom-services.d
	mkdir -p ./etc/sonarr/custom-cont-init.d

	if [ -z "$$(ls -A ./etc/sonarr/custom-services.d 2>/dev/null)" ]; then \
		echo "custom-services.d is empty → downloading scripts_init.bash"; \
		wget -q -P ./etc/sonarr/custom-cont-init.d \
			https://raw.githubusercontent.com/RandomNinjaAtk/arr-scripts/main/sonarr/scripts_init.bash; \
	else \
		echo "custom-services.d has content → skipping download and cleaning old init script"; \
		if [ -f ./etc/sonarr/custom-cont-init.d/scripts_init.bash ]; then \
			rm -f ./etc/sonarr/custom-cont-init.d/scripts_init.bash; \
			echo "Removed ./etc/sonarr/custom-cont-init.d/scripts_init.bash"; \
		fi; \
	fi

	if [ ! -f ./etc/sonarr/extended.conf ]; then \
		echo "extended.conf not found → creating from template"; \
		cp ./templates/sonarr_extended.template ./etc/sonarr/extended.conf; \
	else \
		echo "extended.conf already exists → skipping creation"; \
	fi
	chown -R $USER:$USER ./etc/sonarr
	chmod g+s ./etc/sonarr

#$(info "builders.mk loaded")
