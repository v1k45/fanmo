#!/bin/bash
# Script to pull in new code and restarting the containers

sudo docker-compose -f dev.yml stop
git pull
sudo docker-compose -f dev.yml build
sudo docker-compose -f dev.yml up -d
