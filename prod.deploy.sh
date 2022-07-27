#!/bin/bash
# Script to pull in new code and restarting the containers

set -o errexit
set -o pipefail
set -o nounset

git pull

sudo ln -sf ./deploy/conf/Caddyfile /etc/caddy/Caddyfile
sudo caddy reload

sudo docker stack deploy --compose-file production.yml fanmo --with-registry-auth
