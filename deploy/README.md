# Deployment scripts

Production Deployments are handled by AWS CDK. The `cdk.json` file tells the CDK Toolkit how to execute your app. The build step is not required when using JavaScript.

## Useful commands

* `npm run test`         perform the jest unit tests
* `cdk deploy`           deploy this stack to your default AWS account/region
* `cdk diff`             compare deployed stack with current state
* `cdk synth`            emits the synthesized CloudFormation template


## Manual pre-requsites

* AWS Key pair with name `fanmo.pem`.
* AWS Parameters:
    * gh-deploy-token: Github deploy key for pulling code
    * docker-token: Docker API Token for pulling docker images
    * /django/settings: Django settings env file


### Sample /django/settings

```
# General
# ------------------------------------------------------------------------------
DJANGO_ALLOWED_HOSTS=domainname.com,fanmo.in,localhost,django
USE_DOCKER=yes
DJANGO_DEBUG=no
STAGE=prod
IPYTHONDIR=/app/.ipython
DJANGO_SECRET_KEY=prod_<key>
DOMAIN_NAME=fanmo.in
STORAGE_BUCKET_NAME=change-this-manually-after-inital-deploy
DJANGO_ADMIN_URL=admin/
DJANGO_SETTINGS_MODULE=config.settings.production
DATABASE_URL=postgres://postgres:<get-secret-from-secrets-manager-after-initial-deploy>@change-this-from-secrets.ap-south-1.rds.amazonaws.com:5432/fanmo
DJANGO_AWS_S3_REGION_NAME=ap-south-1
AWS_DEFAULT_REGION=ap-south-1
DJANGO_SECURE_SSL_REDIRECT=no

# Third party
# ------------------------------------------------------------------------------
GOOGLE_OAUTH2_CLIENT_ID=<change-this>
GOOGLE_OAUTH2_SECRET=<change-this>

FACEBOOK_OAUTH2_CLIENT_ID=<change-this>
FACEBOOK_OAUTH2_SECRET=<change-this>

DISCORD_OAUTH2_CLIENT_ID=change-this
DISCORD_OAUTH2_SECRET=change-this-to-secret

RAZORPAY_KEY=<change-this>
RAZORPAY_SECRET=<change-this>
RAZORPAY_WEBHOOK_SECRET=<change-this>

SENTRY_DSN=<change-this>

# Redis
# ------------------------------------------------------------------------------
REDIS_URL=redis://host.docker.internal:6379/0

# Cloudfront
# ------------------------------------------------------------------------------
DJANGO_AWS_S3_CUSTOM_DOMAIN=change-this-after-inital-deploy.cloudfront.net
AWS_CLOUDFRONT_KEY_ID=K7S3-change-this-after-initial-deply
AWS_CLOUDFRONT_KEY=-----BEGIN RSA PRIVATE KEY-----\nMIIEpyNk<change-this-to-single-line-pvt-key>Xq1H7C\n-----END RSA PRIVATE KEY-----\n
```
