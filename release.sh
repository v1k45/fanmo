#!/bin/bash
# Script to build and push fanmo

docker build -f compose/production/django/Dockerfile . -t v1k45/fanmo:dev-latest --build-arg BUILD_ENVIRONMENT=local
docker build -f compose/production/django/Dockerfile . -t v1k45/fanmo:latest --build-arg BUILD_ENVIRONMENT=production
docker push v1k45/fanmo:dev-latest
docker push v1k45/fanmo:latest
