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

create-nfs-backup: sietch-build ## create backup and copy to NFS server
	$(SIETCH_RUN) python /scripts/backup.py create-nfs

create-nfs-backup-direct: sietch-build ## create backup directly on NFS server
	$(SIETCH_RUN) python /scripts/backup.py create-nfs --direct

restore-backup: sietch-build ## restore the latest backup
	$(SIETCH_RUN) python /scripts/backup.py restore --latest

restore-backup-service: sietch-build ## restore the latest backup of a specific service
	$(SIETCH_RUN) python /scripts/backup.py restore --latest --service $(SERVICE_PASSED_DNCASED)

restore-nfs-backup: sietch-build ## restore the latest backup from NFS server
	$(SIETCH_RUN) python /scripts/backup.py restore-nfs

list-backups: sietch-build ## list available backups
	$(SIETCH_RUN) python /scripts/backup.py list

list-nfs-backups: sietch-build ## list backups on NFS server
	$(SIETCH_RUN) python /scripts/backup.py list --location nfs
