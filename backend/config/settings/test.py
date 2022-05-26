"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="uS4NKyRtwJqaYs3MHacspJIhiuYdnoQOghOUoUOv0bZh42kBnVC0xsKUa9AYOL0Z",
)
HASHID_FIELD_SALT = env(
    "HASHID_FIELD_SALT", default="e^h6=azhukkwxqz&%d4vvq7o2_2w_&=o$rt4vx)zdx-d9pf&66"
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[-1]["OPTIONS"]["loaders"] = [  # type: ignore[index] # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

VERSATILEIMAGEFIELD_SETTINGS = {"create_images_on_demand": False}

# Razorpay
# ------------------------------------------------------------------------------
RAZORPAY_KEY = "rzp_test_key"
RAZORPAY_SECRET = "rzp_secret"
RAZORPAY_WEBHOOK_SECRET = "rzp_webook_secret"

# Django Q
# ------------------------------------------------------------------------------
Q_CLUSTER["sync"] = True

# Your stuff...
# ------------------------------------------------------------------------------
