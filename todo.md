# To do

- [x] Recreate the env template into a yaml format.
- [ ] Rewrite tasks and services definitions such that the Docker compose files are in a separate directory path than the persistent data. (/apps/etc and /apps/services)
- [ ] Rewrite service definitions to use jinja variables.
- [ ] Create roles to handle the various onramp tasks (starting all containers, stopping all, creating backups, updating containers.)
- [ ] Consider helper scripts for creating external services.
- [ ] Write documentation

# Other ideas

- The 'logs' tag should automatically enable and start a Dozzle container.
- The playbook should set up some common tasks such as scheduling weekly cleanups of unused container images. It will also install Docker if it's not installed already, and add the current user to the docker group (provided it's not running as root.)
