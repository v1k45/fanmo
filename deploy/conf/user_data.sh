#!/usr/bin/env bash

# install base packages
apt-get -qq update
apt-get -qq -y install apt-transport-https ca-certificates curl gnupg-agent software-properties-common python3-pip at

# install aws cli
pip install --upgrade pip &> /dev/null
pip install awscli --ignore-installed six > /dev/null

# install docker and compose
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt-get -qq update
apt-get -qq -y install docker-ce docker-compose-plugin

# install redis
apt-get -qq -y install redis-server redis-tools

# install caddy
apt-get -qq install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get -qq update
apt-get -qq -y install caddy

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
cp /home/ubuntu/memberships/deploy/conf/fanmo.cron /etc/cron.d/fanmo

# setup redis
cp /home/ubuntu/memberships/deploy/conf/redis.conf /etc/redis/redis.conf
chown redis:redis /etc/redis/redis.conf
systemctl enable redis-server 
systemctl restart redis-server 

# setup caddy
cp /home/ubuntu/memberships/deploy/conf/Caddyfile.prod /etc/caddy/Caddyfile
chown caddy:caddy /etc/caddy/Caddyfile
systemctl restart caddy

# setup docker
aws ssm get-parameter --name "docker-token" --output text --query Parameter.Value --region ap-south-1 | docker login -u v1k45 -p --password-stdin
docker swarm init
docker swarm join-token manager
