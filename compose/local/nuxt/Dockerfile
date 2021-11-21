FROM node:14-alpine

WORKDIR /app

COPY ./frontend/package.json .
RUN yarn install

ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/ .
RUN yarn generate
COPY ./frontend/ .

CMD [ "yarn", "start" ]
