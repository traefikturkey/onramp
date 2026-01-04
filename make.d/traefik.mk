#########################################################
##
## Traefik External DNS Sync
##
## Syncs Traefik external Host() rules to Joyride DNS.
## Extracts hostnames from external-enabled/*.yml and
## writes them to etc/joyride/hosts.d/hosts.
##
#########################################################

traefik-sync-dns: sietch-build ## Sync Traefik external hosts to Joyride DNS
	$(SIETCH_RUN) python /scripts/traefik_hosts.py sync

.PHONY: traefik-sync-dns
