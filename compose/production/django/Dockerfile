ARG PYTHON_VERSION=3.10-slim-buster
ARG NODE_VERSION=14-alpine

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  curl git wget \
  # psycopg2 dependencies
  libpq-dev

# Install Python Dependencies
COPY ./backend/requirements .
# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${BUILD_ENVIRONMENT}.txt

# Build UI
FROM node:${NODE_VERSION} as node-build-stage

WORKDIR /app
COPY ./frontend/package.json .
COPY ./frontend/yarn.lock .
RUN yarn install
ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/ .

RUN yarn generate

# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # image processing
  curl \
  git \
  wget \
  libmagic-dev \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/

# Install nuxt-start
RUN curl -fsSL https://deb.nodesource.com/setup_14.x | bash - && apt-get install -y nodejs
RUN npm install --global yarn
RUN yarn add nuxt-start 
ENV PATH="$PATH:./node_modules/.bin"

COPY --chown=django:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# copy application code to WORKDIR
COPY --chown=django:django ./frontend/nuxt.config.js ${APP_HOME}
# copy nuxt generated files
COPY --chown=django:django --from=node-build-stage /var/www/html /var/www/html/

COPY --chown=django:django ./backend ${APP_HOME}
# make django owner of the WORKDIR directory as well.
RUN chown django:django ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint"]
