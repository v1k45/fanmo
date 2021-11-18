FROM node:14-alpine

WORKDIR /app

COPY ./frontend/package.json .
RUN yarn install

ENV PATH /app/node_modules/.bin:$PATH
COPY ./frontend/ .
RUN rm -r /app/dist
RUN yarn generate

CMD [ "yarn", "start" ]
