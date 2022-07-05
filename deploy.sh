#!/bin/bash
# Script to pull in new code and restarting the containers

git pull
sudo docker stack deploy --compose-file dev.yml memberships
