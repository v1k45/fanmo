#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Inspired by https://axellarsson.com/blog/tag-docker-image-with-git-commit-hash/
bumpver update -v
eval $(bumpver show -n --env)
BUILD_TIMESTAMP=$( date '+%F_%H:%M:%S' )
REPO="v1k45/fanmo:"

DEV_TAG="${REPO}${CURRENT_VERSION}-dev"
DEV_LATEST="${REPO}latest-dev"
DOCKER_BUILDKIT=0
COMPOSE_DOCKER_CLI_BUILD=0
docker build -f compose/production/django/Dockerfile -t "$DEV_TAG" -t "$DEV_LATEST" --build-arg VERSION="$CURRENT_VERSION" --build-arg BUILD_TIMESTAMP="$BUILD_TIMESTAMP" --build-arg BUILD_ENVIRONMENT=local .
docker push "$DEV_LATEST"
docker push "$DEV_TAG" 
git push origin master
