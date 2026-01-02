#########################################################
##
## backup and restore commands
##
#########################################################

backups: ## create backups folder
	mkdir -p ./backups

create-backup: sietch-build backups ## create a backup of the onramp config
	$(SIETCH_RUN) python /scripts/backup.py create

create-backup-service: sietch-build backups ## create a backup of a specific service
	$(SIETCH_RUN) python /scripts/backup.py create --service $(SERVICE_PASSED_DNCASED)

restore-backup: sietch-build ## restore the latest backup (or specific: BACKUP=filename)
ifdef BACKUP
	$(SIETCH_RUN) python /scripts/backup.py restore --file /backups/$(BACKUP)
else
	$(SIETCH_RUN) python /scripts/backup.py restore --latest
endif

restore-backup-service: sietch-build ## restore the latest backup of a specific service
	$(SIETCH_RUN) python /scripts/backup.py restore --latest --service $(SERVICE_PASSED_DNCASED)

list-backups: sietch-build ## list available backups
	$(SIETCH_RUN) python /scripts/backup.py list

#########################################################
##
## NFS backup commands
##
## Uses Docker Compose with NFS volume driver for backup storage.
## Just works if NFS_SERVER and NFS_BACKUP_PATH are configured
## in services-enabled/.env.nfs
##
#########################################################

# Compose command for NFS backup operations
SIETCH_NFS_COMPOSE := $(DOCKER_COMPOSE) $(GLOBAL_ENV_FLAGS) \
	-f sietch/docker-compose.yml \
	-f overrides-available/sietch-nfs-backup.yml

# Helper to check NFS config (reads from env file directly)
define check_nfs_config
	@NFS_SERVER=$$(grep -h '^NFS_SERVER=' services-enabled/.env.nfs 2>/dev/null | cut -d= -f2 | tr -d ' "'); \
	NFS_BACKUP_PATH=$$(grep -h '^NFS_BACKUP_PATH=' services-enabled/.env.nfs 2>/dev/null | cut -d= -f2 | tr -d ' "'); \
	if [ -z "$$NFS_SERVER" ] || [ -z "$$NFS_BACKUP_PATH" ]; then \
		echo "NFS backup requires NFS_SERVER and NFS_BACKUP_PATH."; \
		echo ""; \
		echo "Configure in services-enabled/.env.nfs:"; \
		echo "  make edit-env-nfs"; \
		echo "  Set NFS_SERVER=your-nas-hostname"; \
		echo "  Set NFS_BACKUP_PATH=/path/to/backup/share"; \
		exit 1; \
	fi
endef

create-nfs-backup: sietch-build backups ## create backup and copy to NFS server
	$(check_nfs_config)
	$(SIETCH_NFS_COMPOSE) run --rm sietch python /scripts/backup.py create-nfs

restore-nfs-backup: sietch-build ## restore the latest backup from NFS server
	$(check_nfs_config)
	$(SIETCH_NFS_COMPOSE) run --rm sietch python /scripts/backup.py restore-nfs

list-nfs-backups: sietch-build ## list backups on NFS server
	$(check_nfs_config)
	$(SIETCH_NFS_COMPOSE) run --rm sietch python /scripts/backup.py list --location nfs
