#########################################################
##
## build related commands
##
#########################################################

ifneq (,$(wildcard ./services-enabled/geopulse.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),generate-geopulse-keys)
endif

generate-geopulse-keys:
	@mkdir -p ./etc/geopulse/keys
	./make.d/scripts/generate-geopulse-keys.sh

ifneq (,$(wildcard ./services-enabled/radarr.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),build_radarr_dirs)
endif

build_radarr_dirs:
	@mkdir -p ./etc/radarr/custom-services.d
	@mkdir -p ./etc/radarr/custom-cont-init.d
	@if [ -z "$$(ls -A ./etc/radarr/custom-services.d 2>/dev/null)" ]; then \
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
	@chown -R $$USER:$$USER ./etc/radarr 2>/dev/null || true
	@chmod g+s ./etc/radarr

ifneq (,$(wildcard ./services-enabled/sonarr.yml))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),build_sonarr_dirs)
endif

build_sonarr_dirs:
	@mkdir -p ./etc/sonarr/custom-services.d
	@mkdir -p ./etc/sonarr/custom-cont-init.d
	@if [ -z "$$(ls -A ./etc/sonarr/custom-services.d 2>/dev/null)" ]; then \
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
	@chown -R $$USER:$$USER ./etc/sonarr 2>/dev/null || true
	@chmod g+s ./etc/sonarr

#$(info "builders.mk loaded")
