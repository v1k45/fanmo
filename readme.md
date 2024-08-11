## Fanmo

[Fanmo](https://fanmo.in) is a membership and donations platform designed for creators, similar to Patreon, Ko-fi, and Buy Me a Coffee. Built with Django and Vue.js, Fanmo integrates Razorpay for seamless payment processing.

Fanmo allows creators to set up a personalized page to list membership tiers and accept donations. Fans can support their favorite creators by subscribing to memberships or making one-time donations. Creators, in turn, can offer exclusive content to their members based on tier levels and provide special rewards to donors.

Fanmo was developed with Indian creators in mind, leveraging Razorpay for reliable payment handling.

Created by [@v1k45](https://github.com/v1k45) and [@dumptyd](https://github.com/dumptyd).

## Why Open Source?

Fanmo is being open-sourced due to the unfortunate need to shut it down.

The main issue arose when Razorpay unexpectedly stopped supporting Fanmo’s payment account. Despite multiple attempts to resolve the issue, Razorpay remained unresponsive, rendering Fanmo unable to process payments. Additionally, the platform struggled to gain traction due to limited marketing resources.

By open-sourcing Fanmo, I hope it can benefit others. I'm proud of the work put into this project and would rather share it with the community than let it rot in a private repository.

## How It’s Built

Fanmo’s backend is powered by Django and Django Rest Framework, while the frontend is developed using Vue.js. Payments are managed through Razorpay.

### Backend

The backend code is located in the `backend` directory, with the core Django project in `backend/fanmo`:

- `fanmo/memberships`: Manages memberships, tiers, and subscriptions.
- `fanmo/posts`: Handles creator posts and comments.
- `fanmo/users`: Manages user authentication and preferences.
- `fanmo/donations`: Contains the donation model.
- `fanmo/payments`: Manages payment and payout processes.
- `fanmo/analytics`: Provides basic analytics on memberships and donations.

### Frontend

The frontend code is in the `frontend` directory, built with Vue.js and Nuxt.js:

- `frontend/components/fm`: Custom design system components.
- `frontend/components`: General components.
- `frontend/pages`: Route definitions.
- `frontend/store`: Vuex store for state management.
- `frontend/utils`: Utility functions.
- `frontend/plugins` and `frontend/middleware`: Nuxt.js plugins and middleware.

### Documentation

Product documentation is available in the `docs` directory, created using Astro. It provides an overview of features and usage instructions.

### Email Templates

Email templates are located in the `maizzle` directory, built using Maizzle. The setup is simple but requires manual building of templates, which are then integrated into the Django project.

### Deployment

Deployment is managed on AWS using CDK (Cloud Development Kit) for infrastructure as code. The infrastructure setup is in the `deploy` directory.

- `deploy/fanmo-stack.js`: Contains the CDK stack for backend deployment, including RDS, EC2, S3, CDN, ElasticIP, and SSM for configuration storage.
- `user_data.sh`: Script for setting up the EC2 instance, installing dependencies, and running the Django server.

Fanmo runs in a Docker container, deployed using Docker Swarm for scalability and easy updates. The production Docker image is built using `compose/production/django/Dockerfile`, and static files are served using WhiteNoise.

Deployment flow:

1. Manually build and push the Docker image to DockerHub using the `release.sh` script.
2. Update the image tag in the `production.yml` docker-compose file and push to GitHub.
3. The EC2 instance periodically pulls the latest docker-compose file, updates the image, and restarts the service. Alternatively, the `prod.deploy.sh` script can be run for manual updates.

Caddy Server is used to proxy the Django server, with the configuration in the `deploy/conf/Caddyfile`.

## Running Fanmo Locally

To run Fanmo locally:

1. Start the backend:

```bash
docker-compose -f local.yml up
```

Visit `https://localhost:7777`. If you encounter an SSL error, type `thisisunsafe` to bypass it.

2. Start the frontend:

```bash
cd frontend
yarn dev
```

Update the frontend configuration to point to the backend by setting the `API_URL` to proxy API requests.
