#########################################################
#
# backup and restore up commands
#
#########################################################

create-backup: backups
	sudo tar --exclude=.keep -czf ./backups/onramp-config-backup-$(HOST_NAME)-$(shell date +'%y-%m-%d-%H%M').tar.gz ./etc ./services-enabled ./overrides-enabled ./environments-enabled ./media/databases || true

create-nfs-backup: create-backup
	sudo mount -t nfs $(NFS_SERVER):$(NFS_BACKUP_PATH) $(NFS_BACKUP_TMP_DIR)
	sudo mv ./backups/onramp-config-backup* $(NFS_BACKUP_TMP_DIR)
	sudo umount $(NFS_BACKUP_TMP_DIR)

backups:
	mkdir -p ./backups/

restore-backup:
	sudo tar -xvf ./backups/onramp-config-backup-$(HOST_NAME)-*.tar.gz

$(NFS_BACKUP_TMP_DIR):
	sudo mkdir -p $(NFS_BACKUP_TMP_DIR)
	sudo mount -t nfs $(NFS_SERVER):$(NFS_BACKUP_PATH) $(NFS_BACKUP_TMP_DIR)
	
restore-nfs-backup: $(NFS_BACKUP_TMP_DIR) backups
	$(eval BACKUP_FILE := $(shell find $(NFS_BACKUP_TMP_DIR)/*$(HOST_NAME)* -type f -printf "%T@ %p\n" | sort -n | cut -d' ' -f 2- | tail -n 1))
	sudo rm -rf ./backups/*
	cp -p  $(BACKUP_FILE) ./backups/
	sudo tar -xvf ./backups/*
	echo $(shell basename $(BACKUP_FILE)) > .restore_latest
	sudo umount $(NFS_BACKUP_TMP_DIR)
	sudo rm -r $(NFS_BACKUP_TMP_DIR)
	echo -n "Please run 'make restart' to apply restored backup"	