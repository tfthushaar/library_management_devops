#!/usr/bin/env bash
set -euo pipefail

INVENTORY_FILE="${1:-ansible/inventory/inventory.ini}"
echo "Verifying green environment through Ansible on the target host."
ansible green -i "${INVENTORY_FILE}" -b -m ansible.builtin.uri -a "url=http://127.0.0.1/health status_code=200 return_content=yes"
