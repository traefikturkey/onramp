#########################################################
#
# cloudflare tunnel commands
#
#########################################################

CLOUDFLARE_CMD = $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) run --rm cloudflare-tunnel

./etc/cloudflare-tunnel/cert.pem:
	$(CLOUDFLARE_CMD) login

create-tunnel: ./etc/cloudflare-tunnel/cert.pem
	$(CLOUDFLARE_CMD) tunnel create $(CLOUDFLARE_TUNNEL_NAME)
	$(CLOUDFLARE_CMD) tunnel route dns $(CLOUDFLARE_TUNNEL_NAME) $(CLOUDFLARE_TUNNEL_HOSTNAME)

delete-tunnel:
	$(CLOUDFLARE_CMD) tunnel cleanup $(CLOUDFLARE_TUNNEL_NAME)
	$(CLOUDFLARE_CMD) tunnel delete $(CLOUDFLARE_TUNNEL_NAME)

show-tunnel:
	$(CLOUDFLARE_CMD) tunnel info $(CLOUDFLARE_TUNNEL_NAME)