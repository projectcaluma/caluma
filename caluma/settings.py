import os
import re

import environ
from django.conf import global_settings
from promise import async_instance

env = environ.Env()
django_root = environ.Path(__file__) - 2

ENV_FILE = env.str("ENV_FILE", default=django_root(".env"))
if os.path.exists(ENV_FILE):  # pragma: no cover
    environ.Env.read_env(ENV_FILE)

# per default production is enabled for security reasons
# for development create .env file with ENV=development
ENV = env.str("ENV", "production")


def default(default_dev=env.NOTSET, default_prod=env.NOTSET):
    """Environment aware default."""
    return default_prod if ENV == "production" else default_dev


SECRET_KEY = env.str("SECRET_KEY", default=default("uuuuuuuuuu"))
DEBUG = env.bool("DEBUG", default=default(True, False))
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=default(["*"]))


# Application definition

INSTALLED_APPS = [
    "django.contrib.postgres",
    "localized_fields",
    "psqlextra",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "graphene_django",
    "simple_history",
    "caluma.caluma_core.apps.DefaultConfig",
    "caluma.caluma_user.apps.DefaultConfig",
    "caluma.caluma_form.apps.DefaultConfig",
    "caluma.caluma_workflow.apps.DefaultConfig",
    "caluma.caluma_data_source.apps.DefaultConfig",
]

if DEBUG:
    INSTALLED_APPS.append("django_extensions")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "caluma.urls"
WSGI_APPLICATION = "caluma.wsgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [django_root("caluma", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": env.str("DATABASE_NAME", default="caluma"),
        "USER": env.str("DATABASE_USER", default="caluma"),
        "PASSWORD": env.str("DATABASE_PASSWORD", default=default("caluma")),
        "HOST": env.str("DATABASE_HOST", default="localhost"),
        "PORT": env.str("DATABASE_PORT", default=""),
    }
}

# Cache
# https://docs.djangoproject.com/en/1.11/ref/settings/#caches

CACHES = {
    "default": {
        "BACKEND": env.str(
            "CACHE_BACKEND", default="django.core.cache.backends.locmem.LocMemCache"
        ),
        "LOCATION": env.str("CACHE_LOCATION", ""),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/


def parse_languages(languages):
    return [(language, language) for language in languages]


LANGUAGE_CODE = env.str("LANGUAGE_CODE", "en")
LANGUAGES = (
    parse_languages(env.list("LANGUAGES", default=[])) or global_settings.LANGUAGES
)

TIME_ZONE = env.str("TIME_ZONE", "UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Managing files

MEDIA_STORAGE_SERVICE = env.str("MEDIA_STORAGE_SERVICE", default="minio")
MINIO_STORAGE_ENDPOINT = env.str("MINIO_STORAGE_ENDPOINT", default="minio:9000")
MINIO_STORAGE_ACCESS_KEY = env.str("MINIO_STORAGE_ACCESS_KEY", default="minio")
MINIO_STORAGE_SECRET_KEY = env.str("MINIO_STORAGE_SECRET_KEY", default="minio123")
MINIO_STORAGE_USE_HTTPS = env.str("MINIO_STORAGE_USE_HTTPS", default=False)
MINIO_STORAGE_MEDIA_BUCKET_NAME = env.str(
    "MINIO_STORAGE_MEDIA_BUCKET_NAME", default="caluma-media"
)
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = env.str(
    "MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET", default=True
)
MINIO_PRESIGNED_TTL_MINUTES = env.str("MINIO_PRESIGNED_TTL_MINUTES", default=15)


def parse_admins(admins):  # pragma: no cover
    """
    Parse env admins to django admins.

    Example of ADMINS environment variable:
    Test Example <test@example.com>,Test2 <test2@example.com>
    """
    result = []
    for admin in admins:
        match = re.search(r"(.+) \<(.+@.+)\>", admin)
        if not match:
            raise environ.ImproperlyConfigured(
                'In ADMINS admin "{0}" is not in correct '
                '"Firstname Lastname <email@example.com>"'.format(admin)
            )
        result.append((match.group(1), match.group(2)))
    return result


ADMINS = parse_admins(env.list("ADMINS", default=[]))


# GraphQL

GRAPHENE = {"SCHEMA": "caluma.schema.schema", "MIDDLEWARE": []}

if DEBUG:
    GRAPHENE["MIDDLEWARE"].append("graphene_django.debug.DjangoDebugMiddleware")

# OpenID connect

OIDC_USERINFO_ENDPOINT = env.str("OIDC_USERINFO_ENDPOINT", default=None)
OIDC_VERIFY_SSL = env.bool("OIDC_VERIFY_SSL", default=True)
OIDC_GROUPS_CLAIM = env.str("OIDC_GROUPS_CLAIM", default="caluma_groups")
OIDC_USERNAME_CLAIM = env.str("OIDC_USERNAME_CLAIM", default="sub")
OIDC_BEARER_TOKEN_REVALIDATION_TIME = env.int(
    "OIDC_BEARER_TOKEN_REVALIDATION_TIME", default=0
)

OIDC_INTROSPECT_ENDPOINT = env.str("OIDC_INTROSPECT_ENDPOINT", default=None)
OIDC_INTROSPECT_CLIENT_ID = env.str("OIDC_INTROSPECT_CLIENT_ID", default=None)
OIDC_INTROSPECT_CLIENT_SECRET = env.str("OIDC_INTROSPECT_CLIENT_SECRET", default=None)

# Extensions

VISIBILITY_CLASSES = env.list(
    "VISIBILITY_CLASSES", default=default(["caluma.caluma_core.visibilities.Any"])
)

PERMISSION_CLASSES = env.list(
    "PERMISSION_CLASSES", default=default(["caluma.caluma_core.permissions.AllowAny"])
)

VALIDATION_CLASSES = env.list("VALIDATION_CLASSES", default=[])

DATA_SOURCE_CLASSES = env.list("DATA_SOURCE_CLASSES", default=[])

FORMAT_VALIDATOR_CLASSES = env.list("FORMAT_VALIDATOR_CLASSES", default=[])

# Cors headers
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])

# simple history
SIMPLE_HISTORY_HISTORY_ID_USE_UUID = True

# Historical API
ENABLE_HISTORICAL_API = env.bool("ENABLE_HISTORICAL_API", default=False)

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "": {"handlers": ["console"], "level": env.str("LOG_LEVEL", default="INFO")}
    },
}

# Configure the fields you intend to use in the "meta" fields. This will
# provide corresponding constants in the ordreBy filter.
META_FIELDS = env.list("META_FIELDS", default=[])


# static files

STATIC_URL = "/static/"

# disable trampoline to improve performance
# see https://github.com/graphql-python/graphene/issues/268
# this means though that data loader won't work which we currently don't use
# best to remove once graphql-core-next is compatible with graphene.
async_instance.disable_trampoline()
