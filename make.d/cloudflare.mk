#########################################################
#
# cloudflare tunnel commands
#
# Note: Tunnel creation/deletion uses cloudflared CLI via docker.
# DNS API operations use the Python cloudflare.py script.
#
#########################################################

create-tunnel: etc/cloudflared etc/cloudflared/cert.pem etc/cloudflared/%.json ## create the cloudflare tunnel and dns entry

etc/cloudflared:
	mkdir -p ./etc/cloudflared
	sudo chown -R 65532:$(USER) ./config/cloudflared
	sudo chmod 770 ./config/cloudflared

etc/cloudflared/cert.pem:
	$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel login
	sudo chown -R 65532:$(USER) ./config/cloudflared
	sudo chmod 660 ./config/cloudflared/*

etc/cloudflared/%.json:
	@echo "Creating Cloudflared Tunnel $(CLOUDFLARE_TUNNEL_URL)"
	$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel create $(CLOUDFLARE_TUNNEL_NAME)
	$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel route dns $(CLOUDFLARE_TUNNEL_NAME) $(CLOUDFLARE_TUNNEL_URL)
	sudo chown -R 65532:$(USER) ./config/cloudflared
	sudo chmod 660 ./config/cloudflared/*

remove-tunnel: remove-cloudflare-dns-entry remove-cloudflare-tunnel ## remove the cloudflare tunnel and dns entry

remove-cloudflare-tunnel: ## remove the cloudflare tunnel
	@echo "Removing Cloudflared Tunnel $(CLOUDFLARE_TUNNEL_URL)"
	-$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel cleanup $(CLOUDFLARE_TUNNEL_NAME)
	-$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel delete $(CLOUDFLARE_TUNNEL_NAME)
	-rm -rf ./config/cloudflare/*.json

remove-cloudflare-dns-entry: sietch-build ## remove the cloudflare DNS entry via API
	$(SIETCH_RUN) python /scripts/cloudflare.py dns delete --name $(CLOUDFLARE_TUNNEL_URL)

list-cloudflare-dns: sietch-build ## list cloudflare DNS records
	$(SIETCH_RUN) python /scripts/cloudflare.py dns list

show-tunnel: ## show the status of the cloudflare tunnel
	@echo "Checking Cloudflared Tunnel $(CLOUDFLARE_TUNNEL_URL)"
	-$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel info $(CLOUDFLARE_TUNNEL_NAME) || echo $$?

show-cloudflare-zone: sietch-build ## show cloudflare zone info
	$(SIETCH_RUN) python /scripts/cloudflare.py zone info
