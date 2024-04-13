#########################################################
## 
## backup and restore up commands 
##
#########################################################

$(NFS_BACKUP_TMP_DIR):
	sudo mkdir -p $(NFS_BACKUP_TMP_DIR)
	sudo mount -t nfs $(NFS_SERVER):$(NFS_BACKUP_PATH) $(NFS_BACKUP_TMP_DIR)
	
create-backup: backups ## create a backup of the onramp config
	sudo tar --exclude=.keep $(ONRAMP_BACKUP_EXCLUSIONS:=--exclude=etc/plex/Library) -czf ./backups/onramp-config-backup-$(HOST_NAME)-$(shell date +'%y-%m-%d-%H%M').tar.gz ./etc ./services-enabled ./overrides-enabled ./environments-enabled $(ONRAMP_BACKUP_INCLUSIONS) || true

create-nfs-backup: $(NFS_BACKUP_TMP_DIR) create-backup ## create a backup of the onramp config and copy it to the nfs server
	sudo mv ./backups/onramp-config-backup* $(NFS_BACKUP_TMP_DIR)
	sudo umount $(NFS_BACKUP_TMP_DIR)

backups: ## create backups folder
	mkdir -p ./backups/

restore-backup: ## restore the latest backup of the onramp config
	sudo tar -xvf ./backups/onramp-config-backup-$(HOST_NAME)-*.tar.gz

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