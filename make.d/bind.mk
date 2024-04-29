setup-bind: netplan-apply
	$(make) enable-service bind
	$(make) start-service  bind

netplan-apply: disable-systemd-resolved
	@echo "Applying netplan"
	@sudo netplan apply

disable-systemd-resolved: stop-systemd-resolved
	@echo "Disabling systemd-resolved"
	@systemctl disable systemd-resolved
	sudo rm /etc/resolv.conf

stop-systemd-resolved:
	@echo "Stopping systemd-resolved"
	@systemctl stop systemd-resolved
