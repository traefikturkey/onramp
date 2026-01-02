#########################################################
#
# n8n workflow management commands
#
# Workflows are stored as JSON files in media/n8n/workflows/
# Use these commands to sync between the filesystem and n8n
#
#########################################################

N8N_CONTAINER := $(shell docker ps -q -f name=n8n -f status=running 2>/dev/null)

n8n-export-workflows: ## Export all n8n workflows to media/n8n/workflows/
ifndef N8N_CONTAINER
	@echo "Error: n8n container is not running"
	@exit 1
endif
	@mkdir -p ./media/n8n/workflows
	docker exec -u node n8n n8n export:workflow --all --separate --output=/home/node/workflows
	@echo "Workflows exported to ./media/n8n/workflows/"

n8n-import-workflows: ## Import workflows from media/n8n/workflows/ into n8n
ifndef N8N_CONTAINER
	@echo "Error: n8n container is not running"
	@exit 1
endif
	docker exec -u node n8n n8n import:workflow --separate --input=/home/node/workflows
	@echo ""
	@echo "Workflows imported. Restart n8n for changes to take effect:"
	@echo "  make restart-service n8n"

n8n-export-credentials: ## Export n8n credentials (encrypted) to media/n8n/workflows/
ifndef N8N_CONTAINER
	@echo "Error: n8n container is not running"
	@exit 1
endif
	@mkdir -p ./media/n8n/workflows
	docker exec -u node n8n n8n export:credentials --all --output=/home/node/workflows/credentials.json
	@echo "Credentials exported to ./media/n8n/workflows/credentials.json"
	@echo "Note: Credentials are encrypted with N8N_ENCRYPTION_KEY"

n8n-import-credentials: ## Import n8n credentials from media/n8n/workflows/
ifndef N8N_CONTAINER
	@echo "Error: n8n container is not running"
	@exit 1
endif
	docker exec -u node n8n n8n import:credentials --input=/home/node/workflows/credentials.json
	@echo ""
	@echo "Credentials imported. Restart n8n for changes to take effect:"
	@echo "  make restart-service n8n"
