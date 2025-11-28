setup-coredns: prep-dns
	mkdir -p ./etc/coredns
	touch ./etc/coredns/Corefile.pihole

prep-dns: 
	sudo sed -i 's/#DNSStubListener=yes/DNSStubListener=no/' /etc/systemd/resolved.conf
	sudo systemctl restart systemd-resolved
