#!/usr/bin/env bash

# install base packages
sudo apt-get -qq update
sudo apt-get -qq -y install apt-transport-https ca-certificates curl gnupg-agent software-properties-common python3-pip at
sudo pip install --upgrade pip &> /dev/null

# install aws cli
sudo pip install awscli --ignore-installed six > /dev/null

# install docker and compose
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get -qq update
sudo apt-get -qq -y install docker-ce
sudo apt-get -qq -y install docker-compose-plugin

# install redis
sudo apt-get -qq -y install redis-server redis-tools

# install caddy
sudo apt-get -qq install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get -qq update
sudo apt-get -qq -y install caddy

# setup github deploy key by fetching it from the SSM store and setting it in 'ubuntu' user's SSH config
aws ssm get-parameter --name "gh-deploy-key" --output text --query Parameter.Value --region ap-south-1 > /home/ubuntu/.ssh/github_rsa
# it's ok to disable StrictHostKeyChecking in this case because we're getting the key from the trusted SSM store.
echo -e "Host github.com\n\tIdentityFile ~/.ssh/github_rsa\n\tIdentitiesOnly yes\n\tStrictHostKeyChecking no\n" >> /home/ubuntu/.ssh/config

# create required directories, clone the repo and setup swarm
sudo -u ubuntu bash -c "
  cd /home/ubuntu/;
  mkdir -p logs;
  git clone git@github.com:v1k45/memberships.git;
  cd memberships;
  sudo at now +10 minutes -f ./prod.deploy.sh;
"

# copy cronjob
sudo ln -sf /home/ubuntu/memberships/deploy/conf/fanmo.cron /etc/cron.d/fanmo

# setup redis
sudo ln -sf /home/ubuntu/memberships/deploy/conf/redis.conf /etc/redis/redis.conf
sudo systemctl enable redis-server 
sudo service redis-server restart

# setup docker
sudo docker swarm init
sudo docker swarm join-token manager
