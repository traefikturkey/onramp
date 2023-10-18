#########################################################
#
# cloudflare tunnel commands
#
#########################################################

create-tunnel: etc/cloudflared etc/cloudflared/cert.pem etc/cloudflared/%.json

etc/cloudflared:
	mkdir -p ./etc/cloudflared
	sudo chown -R 65532:$(USER) ./config/cloudflared
	sudo chmod 770 ./config/cloudflared

etc/cloudflared/cert.pem:
	$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel login
	sudo chown -R 65532:$(USER) ./config/cloudflared
	sudo chmod 660 ./config/cloudflared/*

# using make the way it was intended, only create tunnel if directory does not exist
etc/cloudflared/%.json:
	@echo "Creating Cloudflared Tunnel $(CLOUDFLARE_TUNNEL_URL)"
	$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel create $(CLOUDFLARE_TUNNEL_NAME) 
	$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel route dns $(CLOUDFLARE_TUNNEL_NAME) $(CLOUDFLARE_TUNNEL_URL)
	sudo chown -R 65532:$(USER) ./config/cloudflared
	sudo chmod 660 ./config/cloudflared/*
 
remove-tunnel: remove-cloudflare-dns-entry remove-cloudflare-tunnel 
	
remove-cloudflare-tunnel:
	@echo "Removing Cloudflared Tunnel $(CLOUDFLARE_TUNNEL_URL)"
	-$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel cleanup $(CLOUDFLARE_TUNNEL_NAME)
	-$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel delete $(CLOUDFLARE_TUNNEL_NAME)
	-rm -rf ./config/cloudflare/*.json

# https://stackoverflow.com/a/29085760
# https://stackoverflow.com/a/62819637
# https://gist.github.com/Tras2/cba88201b17d765ec065ccbedfb16d9a?permalink_comment_id=3754799
# https://gist.github.com/slayer/442fa2fffed57f8409e0b23bd0673a92

.ONESHELL:
remove-cloudflare-dns-entry:
		ZONE_ID=$$(curl -sX  GET "https://api.cloudflare.com/client/v4/zones?name=$(HOST_DOMAIN)" -H "Authorization: Bearer $(CF_DNS_API_TOKEN)" -H 'Content-Type: application/json' | jq -r '{"result"}[] | .[0] | .id')
		RECORD_ID=$$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$${ZONE_ID}/dns_records?type=CNAME&name=$(CLOUDFLARE_TUNNEL_URL)" -H "Authorization: Bearer $(CF_DNS_API_TOKEN)" -H "Content-Type: application/json" | jq -r '{"result"}[] | .[0] | .id')
		echo RECORD_ID = $$RECORD_ID
		curl -s -X DELETE "https://api.cloudflare.com/client/v4/zones/$${ZONE_ID}/dns_records/$${RECORD_ID}" -H "Authorization: Bearer $(CF_DNS_API_TOKEN)" -H "Content-Type: application/json"

show-tunnel: 
	@echo "Checking Cloudflared Tunnel $(CLOUDFLARE_TUNNEL_URL)"
	-$(COMPOSE_COMMAND) $(FLAGS) run --rm cloudflared tunnel info $(CLOUDFLARE_TUNNEL_NAME) || echo $$?
	@echo 'command exited with $(.SHELLSTATUS)'