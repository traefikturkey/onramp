#!/usr/bin/env bash

if ! [[ -f ./secrets.yml ]]; then
  cp ./.templates/secrets.template secrets.yml
  chmod 600 secrets.yml
fi

# Check if secrets.yml is already an ansible-vault encrypted file.
if ! head -1 secrets.yml | grep -q "\$ANSIBLE_VAULT" ; then
  echo "File not encrypted with Ansible Vault. Please enter an encryption key when prompted: "
  ansible-vault encrypt secrets.yml
fi

ansible-vault edit secrets.yml
