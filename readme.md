## Fanmo

[fanmo](https://fanmo.in) is a memberships and donations platform, similar to Patreon, Ko-fi, and Buy Me a Coffee. It is built with Django and Vue.js. It uses Razorpay for payments.

The idea is to allow creators to create a page where they can list their membership tiers and accept donations. Fans can then support their favourite creators by becoming members or donating. Creators can offer rewards to their members by creating posts that are visible only to members of a certain tier. They can also offer one-time rewards to donors.

It was made with Indian creators in mind, so it supports Indian payment methods like UPI, netbanking, and wallets.

## Why Open Source?

I am open sourcing this project because I had to shut it down.

The primary reason was that Razorpay for some vague reason decided to stop supporting my account. I tried to get in touch with them multiple times, but they never responded. I had to shut it down because I couldn't accept payments anymore. I also couldn't find many users because I didn't have the resources or knowledge to market it properly.

I am open sourcing it because I think it is a good project and it can be useful to someone. I also want to show my work to the world. I am proud of what I have built, and I want to share it with others.

## How is it built?

The backend is built with Django and Django Rest Framework. The frontend is built with Vue.js. The payments are handled by Razorpay.

### Backend

For backend code, see the `backend` directory. `backend/fanmo` contains the Django project:

- `fanmo/memberships` contains memberships, tiers, and subscriptions.
- `fanmo/posts` contains posts that creators can create, and comments on those posts.
- `fanmo/users` contains has all the user-related stuff like authentication, preferences, etc.
- `fanmo/donations` has the donation model.
- `fanmo/payments` handles payments and payouts.
- `fanmo/analytics` for basic analytics around memberships and donations.

### Frontend

For frontend code, see the `frontend` directory. It is a Vue.js project:

- `frontend/components/fm` contains all components made for the custom design system.
- `frontend/components` for all other components.
- `frontend/pages` for the routes.
- `frontend/store` for the Vuex store.
- `frontend/utils` for utility functions.
- `frontend/plugins` and `frontend/middleware` for Nuxt.js plugins and middleware.

### Documentation

Product documentation is in the `docs` directory. It contains contains overview of the features and how to use them. It is built using Astro.

### Email Templates

Email templates are in the `maizzle` directory. They are built using Maizzle. The setup is very basic, and requires manually building the templates every time. The build templates are then copied to the Django project.

### Deployment

The deployment is done on AWS. CDK is used for infrastructure as code. The infrastructure code is in the `deploy` directory.

`deploy/fanmo-stack.js` contains the CDK stack that deploys the backend. It creates an RDS instance, an EC2 instance, S3 buckets, CDN, ElasticIP, and other necessary resources. It also uses SSM to store configuration values.

The `user_data.sh` script is used to set up the EC2 instance with the necessary dependencies and run the Django server.

The server is run inside a Docker container deployed using Docker Swarm to make it easier to scale or update.

The production Docker image is built using `compose/production/django/Dockerfile`. The docker image also builds the frontend and docs and the static files are served using WhiteNoise.

The deployment flow goes like this:

- The docker image is manually built and pushed DockerHub. `release.sh` script is used for this.
- The docker image tag is updated in the `production.yml` docker-compose file. It is pushed to GitHub.
- The EC2 instance is configured to pull the latest docker-compose file periodically. It then pulls the latest image and restarts the docker service. Otherwise, `prod.deploy.sh` script can be run to manually update the service.

The django server is proxied by Caddy Server. The Caddyfile is in the `deploy/conf/Caddyfile`.

## How to run it?

Locally, you can run the backend and frontend separately. The backend runs on `localhost:7777` and the frontend runs on `localhost:3000`.

You can run the backend using the following commands:

```bash
docker-compose -f local.yml up
```

You can run the frontend using the following commands:

```bash
cd frontend
yarn dev
```

> [!IMPORTANT]  
> The project has been renamed from `memberships` to `fanmo`. So, you may need to update the imports and references accordingly.

### Credits

[@v1k45](https://github.com/v1k45) and [@dumptyd](https://github.com/dumptyd).
