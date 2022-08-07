## Fanmo Backend

### How to run?

```
docker-compose -f local.yml up
```

### How to read

Start from `config/api_router.py`

### How are settings managed?

See environment specific settings under `config/settings/`

- base.py: Common and essential settings and helpers
- local.py: Local env settings
- test.py: Test settings
- prod.py:  Production settings, has different logging, storage, error reporting etc.
- dev.py: Based on prod.py, but mocks object storage and email server.

### Code style

Following tools are recommended, but not enforced yet:

```
black fanmo/
isort fanmo/
flake8 fanmo/
```

### Env vars and secrets

Everthing goes into `.envs/.{stage}/.{component}` files in the project root.

`.envs/.local/.django` has config for local development. 

### New dependencies

Dependencies should be manually added to `requirements/{stage}.txt` files and then the docker image should be rebuilt.

### Email templates

All email templates are written using `maizzle`, the template files in this directory are just the build files spit out by maizzle.

Do not touch `fanmo/templates/maizzle/`, it will be overwritten.

### Media file management

In dev and local, media files are stored in the mounted volume and served using Caddy. In production, S3 is used.

### Tests

Not comprehensive, but critical components are suposed to be at least sanity-checked.

```
pytest
```

### Thirdparty

All payments are processed by Razorpay and code makes heavy assumptions of its reliability.
Emails are sent by AWS SES in production.


### Docker debugging

Drop this code in some module

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
```

Attach VS Code debugger: F5
