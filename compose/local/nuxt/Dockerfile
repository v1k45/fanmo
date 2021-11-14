FROM node:14-alpine
RUN apk update && apk add python3 make g++

RUN mkdir /app
WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/package.json /app/package.json

RUN yarn install --silent

RUN yarn add node-gyp

RUN yarn generate

CMD [ "yarn", "start" ]
