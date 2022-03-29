"""
Base settings to build other settings files upon.
"""
from pathlib import Path

import environ

ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# memberships/
APPS_DIR = ROOT_DIR / "memberships"
PLACEHOLDERS_DIR = APPS_DIR / "static" / "images" / "placeholders"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Asia/Kolkata"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en-us"
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# https://docs.djangoproject.com/en/dev/ref/settings/#locale-paths
LOCALE_PATHS = [str(ROOT_DIR / "locale")]

DOMAIN_NAME = env("DOMAIN_NAME")
# DATABASES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_hotp",
    "django_otp.plugins.otp_email",
    "rest_framework",
    "dj_rest_auth",
    "corsheaders",
    "drf_spectacular",
    "djmoney",
    "versatileimagefield",
    "django_q",
]

LOCAL_APPS = [
    "memberships.users.apps.UsersConfig",
    "memberships.subscriptions.apps.SubscriptionsConfig",
    "memberships.posts.apps.PostsConfig",
    "memberships.payments.apps.PaymentsConfig",
    "memberships.donations",
    "memberships.webhooks",
    "memberships.integrations",
    # Your stuff: custom apps go here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules
MIGRATION_MODULES = {"sites": "memberships.contrib.sites.migrations"}

# AUTHENTICATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-user-model
AUTH_USER_MODEL = "users.User"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url
LOGIN_REDIRECT_URL = "account_login"
# https://docs.djangoproject.com/en/dev/ref/settings/#login-url
LOGIN_URL = "account_login"


# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    # https://docs.djangoproject.com/en/dev/topics/auth/passwords/#using-argon2-with-django
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR / "media")
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "memberships.utils.context_processors.settings_context",
            ],
        },
    }
]

# https://docs.djangoproject.com/en/dev/ref/settings/#form-renderer
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = "bootstrap4"

# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True
# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = [
    "localhost",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-browser-xss-filter
SECURE_BROWSER_XSS_FILTER = True
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SAMESITE = "Strict"

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#email-timeout
EMAIL_TIMEOUT = 5

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = "admin/"
# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [("""Vikas""", "vikas@example.com")]
# https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}

# django-allauth
# ------------------------------------------------------------------------------
# https://django-allauth.readthedocs.io/en/latest/configuration.html
ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_ADAPTER = "memberships.users.adapters.AccountAdapter"
SOCIALACCOUNT_ADAPTER = "memberships.users.adapters.SocialAccountAdapter"
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
OLD_PASSWORD_FIELD_ENABLED = True
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["email", "profile"],
        "APP": {
            "client_id": env("GOOGLE_OAUTH2_CLIENT_ID"),
            "secret": env("GOOGLE_OAUTH2_SECRET"),
        },
    },
    "facebook": {
        "SCOPE": ["email", "public_profile"],
        "APP": {
            "client_id": env("FACEBOOK_OAUTH2_CLIENT_ID"),
            "secret": env("FACEBOOK_OAUTH2_SECRET"),
        },
    },
    "discord_user": {
        "SCOPE": ["email", "identity"],
        "APP": {
            "client_id": env("DISCORD_OAUTH2_CLIENT_ID"),
            "secret": env("DISCORD_OAUTH2_SECRET"),
        },
    },
    "discord_server": {
        "SCOPE": ["email", "identity", "guids", "guilds.join"],
        "APP": {
            "client_id": env("DISCORD_OAUTH2_CLIENT_ID"),
            "secret": env("DISCORD_OAUTH2_SECRET"),
        },
    },
}

# django-rest-framework
# -------------------------------------------------------------------------------
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "memberships.utils.exception_handlers.handle_drf_exception",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Mock token authentication
REST_AUTH_TOKEN_MODEL = "memberships.users.models.User"
REST_AUTH_TOKEN_CREATOR = "memberships.utils.authentication.create_auth_token"
REST_AUTH_SERIALIZERS = {
    "TOKEN_SERIALIZER": "memberships.users.api.serializers.UserSerializer",
    "USER_DETAILS_SERIALIZER": "memberships.users.api.serializers.UserSerializer",
    "PASSWORD_RESET_SERIALIZER": "memberships.users.api.serializers.PasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "memberships.users.api.serializers.PasswordResetConfirmSerializer",
}
REST_AUTH_REGISTER_SERIALIZERS = {
    "REGISTER_SERIALIZER": "memberships.users.api.serializers.RegisterSerializer",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Memberships API",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api",
    "COMPONENT_SPLIT_REQUEST": True,
    # OTHER SETTINGS
}


# money - https://github.com/django-money/django-money
CURRENCIES = ("INR",)
from moneyed import INR

DEFAULT_CURRENCY = INR

# payments
RAZORPAY_KEY = "FANMO_SECRET_CHANGE_ME"
RAZORPAY_SECRET = "FANMO_SECRET_CHANGE_ME"
RAZORPAY_WEBHOOK_SECRET = "FANMO_SECRET_CHANGE_ME"

# business logic
DEFAULT_PLATFORM_FEE_PERCENT = 4.90
MINIMUM_PAYMENT_AMOUNT = 10.00
SUBSCRIPTION_GRACE_PERIOD_DAYS = 3


# django-cors-headers - https://github.com/adamchainz/django-cors-headers#setup
CORS_URLS_REGEX = r"^/api/.*$"

# django-versatileimagefield - https://github.com/respondcreate/django-versatileimagefield
VERSATILEIMAGEFIELD_SETTINGS = {"jpeg_resize_quality": 90}
VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    "user_avatar": [
        ("full", "url"),
        ("medium", "crop__300x300"),
        ("small", "crop__150x150"),
        ("thumbnail", "crop__50x50"),
    ],
    "user_cover": [
        ("full", "url"),
        ("big", "crop__1800x400"),
        ("medium", "crop__900x200"),
        ("small", "crop__300x70"),
    ],
    "tier_cover": [
        ("full", "url"),
    ],
    "post_image": [
        ("full", "url"),
    ],
}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
