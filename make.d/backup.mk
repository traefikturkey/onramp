#########################################################
## 
## backup and restore up commands 
##
#########################################################

# create a backup folder var for the onramp config only for non NFS for now
ONRAMP_BACKUP_LOCATION=./backups

ifdef ONRAMP_BACKUP_LOCATION_ENV
ONRAMP_BACKUP_LOCATION := $(ONRAMP_BACKUP_LOCATION_ENV)
endif

backups: ## create backups folder
	mkdir -p ${ONRAMP_BACKUP_LOCATION}

$(NFS_BACKUP_TMP_DIR):
	sudo mkdir -p $(NFS_BACKUP_TMP_DIR)
	sudo mount -t nfs $(NFS_SERVER):$(NFS_BACKUP_PATH) $(NFS_BACKUP_TMP_DIR)

create-backup: backups ## create a backup of the onramp config
	sudo tar --exclude=.keep $(ONRAMP_BACKUP_EXCLUSIONS:=--exclude=etc/plex/Library) -czf ${ONRAMP_BACKUP_LOCATION}/onramp-config-backup-$(HOST_NAME)-$(shell date +'%y-%m-%d-%H%M').tar.gz ./etc ./services-enabled ./overrides-enabled ./environments-enabled $(ONRAMP_BACKUP_INCLUSIONS) || true

create-backup-service: backups ## create a backup of a service 
ifneq (,$(wildcard ./services-enabled/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Backing up $(SERVICE_PASSED_DNCASED)..."
	sudo tar --exclude=.keep $(ONRAMP_BACKUP_EXCLUSIONS:=--exclude=etc/plex/Library) -czf ${ONRAMP_BACKUP_LOCATION}/onramp-config-backup-$(HOST_NAME)-$(SERVICE_PASSED_DNCASED)-$(shell date +'%y-%m-%d-%H%M').tar.gz ./etc/$(SERVICE_PASSED_DNCASED) || true
else
	@echo "No such service file ./services-enabled/$(SERVICE_PASSED_DNCASED).yml!"
endif

create-nfs-backup: $(NFS_BACKUP_TMP_DIR) create-backup ## create a backup of the onramp config and copy it to the nfs server
	sudo mv ./backups/onramp-config-backup* $(NFS_BACKUP_TMP_DIR)
	sudo umount $(NFS_BACKUP_TMP_DIR)
	sudo rm -r $(NFS_BACKUP_TMP_DIR)

create-nfs-backup-direct: $(NFS_BACKUP_TMP_DIR) ## create a backup of the onramp config directly to the nfs server
	if [ -d $(NFS_BACKUP_TMP_DIR) ]; then
		sudo mount -t nfs $(NFS_SERVER):$(NFS_BACKUP_PATH) $(NFS_BACKUP_TMP_DIR)
	else
		sudo mkdir -p $(NFS_BACKUP_TMP_DIR)
		sudo mount -t nfs $(NFS_SERVER):$(NFS_BACKUP_PATH) $(NFS_BACKUP_TMP_DIR)
		fi
	sudo tar --exclude=.keep $(ONRAMP_BACKUP_EXCLUSIONS:=--exclude=etc/plex/Library) -czf $(NFS_BACKUP_TMP_DIR)/onramp-config-backup-$(HOST_NAME)-$(shell date +'%y-%m-%d-%H%M').tar.gz ./etc ./services-enabled ./overrides-enabled $(ONRAMP_BACKUP_INCLUSIONS) || true
	sudo umount $(NFS_BACKUP_TMP_DIR)
	sudo rm -r $(NFS_BACKUP_TMP_DIR)	

restore-backup: ## restore the latest backup of the onramp config
	sudo tar -xvf $(ONRAMP_BACKUP_LOCATION)/onramp-config-backup-$(HOST_NAME)-*.tar.gz

restore-backup-service: ## restore the latest backup of the onramp config
	sudo tar -xvf $(ONRAMP_BACKUP_LOCATION)/onramp-config-backup-$(HOST_NAME)-$(SERVICE_PASSED_DNCASED)-*.tar.gz

restore-nfs-backup: $(NFS_BACKUP_TMP_DIR) backups ## restore the latest backup of the onramp config from the nfs server
	$(eval BACKUP_FILE := $(shell find $(NFS_BACKUP_TMP_DIR)/*$(HOST_NAME)* -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f 2- | tail -n 1))
	sudo rm -rf ./backups/*
	cp -p  $(BACKUP_FILE) ./backups/
	sudo tar -xvf ./backups/*
	# having issues with basename syntax
	# echo $(shell basename $(BACKUP_FILE)) > .restore_latest
	sudo umount $(NFS_BACKUP_TMP_DIR)
	sudo rm -r $(NFS_BACKUP_TMP_DIR)
	echo -n "Please run 'make restart' to apply restored backup"