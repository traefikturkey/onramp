# OnRamp Ansible Playbooks

These playbooks are designed to help bootstrap a new server for OnRamp, supporting the "Disaster Recovery" philosophy.

## Usage

You can use these playbooks to provision a fresh Ubuntu server before installing OnRamp.

### Common Tasks

- **Install Docker:** `ansible-playbook install-docker.yml`
- **Update Hosts:** `ansible-playbook update-hosts.yml`
- **Install Node Exporter:** `ansible-playbook install-node-exporter.yml`

## Full Rebuild Workflow (Example)

1.  **Provision VM/Hardware:** (e.g., via Terraform or manually)
2.  **Bootstrap OS:** Use these Ansible playbooks to install Docker and dependencies.
3.  **Clone OnRamp:** `git clone https://github.com/traefikturkey/onramp.git`
4.  **Restore Backup:**
    *   Copy your backup tarball to `onramp/backups/`
    *   Run `make restore-backup` inside `onramp/`
5.  **Start Services:** `make restart`

This workflow allows you to recover from a total failure in minutes.
