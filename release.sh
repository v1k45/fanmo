#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

# Inspired by https://axellarsson.com/blog/tag-docker-image-with-git-commit-hash/
bumpver update -v
eval $(bumpver show -n --env)
BUILD_TIMESTAMP=$( date '+%F %H:%M:%S' )
REPO="v1k45/fanmo:"

TAG="${REPO}${CURRENT_VERSION}"
LATEST="${REPO}latest"
DOCKER_BUILDKIT=0
COMPOSE_DOCKER_CLI_BUILD=0
docker build -f compose/production/django/Dockerfile -t "$TAG" -t "$LATEST" --build-arg VERSION="$CURRENT_VERSION" --build-arg BUILD_TIMESTAMP="$BUILD_TIMESTAMP" .
docker push "$LATEST"
docker push "$TAG" 
git push origin master --tags
