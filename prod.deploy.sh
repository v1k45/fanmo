#!/bin/bash

# Script to pull in new code and restarting the containers

set -o errexit
set -o pipefail
set -o nounset

# update code
git pull

# update env settings
aws ssm get-parameter --name "/django/settings" --output text --query Parameter.Value --region ap-south-1 > /home/ubuntu/memberships/.envs/.prod/.django

# update and reload caddy
sudo cp ./deploy/conf/Caddyfile /etc/caddy/Caddyfile
sudo chown -R caddy:caddy /etc/caddy/Caddyfile
sudo systemctl reload caddy

# deploy server
sudo docker stack deploy --compose-file production.yml fanmo --with-registry-auth
