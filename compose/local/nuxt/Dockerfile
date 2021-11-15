FROM node:14-alpine

WORKDIR /app

ENV NODE_ENV=production
COPY ./frontend/package.json .
RUN yarn install

ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/ .

CMD [ "yarn", "start" ]
