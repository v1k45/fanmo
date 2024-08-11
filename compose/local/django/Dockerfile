ARG PYTHON_VERSION=3.10-slim-buster

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  # psycopg2 dependencies
  libpq-dev

# Requirements are installed here to ensure they will be cached.
COPY ./backend/requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${BUILD_ENVIRONMENT}.txt

# Build UI
FROM node:14-alpine as node-build-stage
ARG STAGE=dev
ENV STAGE ${STAGE}
RUN apk add --update python3 make g++ && rm -rf /var/cache/apk/*

WORKDIR /app
COPY ./frontend/package.json .
COPY ./frontend/yarn.lock .
RUN yarn install
ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/ .

RUN yarn generate

# Build docs
FROM node:18-alpine as docs-build-stage
ARG STAGE=prod
ENV STAGE ${STAGE}
RUN apk add --update python3 make g++ && rm -rf /var/cache/apk/*

WORKDIR /app
COPY ./docs/package.json .
COPY ./docs/package-lock.json .
RUN npm install
ENV PATH /app/node_modules/.bin:$PATH
COPY ./docs/ .

RUN npm run build


# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # image processing
  libmagic-dev \
  libmagickwand-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
	&& rm -rf /wheels/

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/local/django/qcluster /qcluster
RUN sed -i 's/\r$//g' /qcluster
RUN chmod +x /qcluster

COPY --from=node-build-stage /app/dist /var/www/html/
COPY --from=docs-build-stage /app/dist /var/www/html/docs/
COPY --chown=django:django ./supervisord.conf /etc/

# # copy application code to WORKDIR
# COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint"]
CMD ["supervisord"]
