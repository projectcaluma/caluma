"""The main settings module used by caluma service."""

import re

from django.conf import global_settings
from promise import async_instance

from .caluma import *  # noqa
from .caluma import GRAPHENE, default, django_root, env, environ

DEBUG = env.bool("DEBUG", default=default(True, False))
SECRET_KEY = env.str("SECRET_KEY", default=default("uuuuuuuuuu"))
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


# Cors headers
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])


# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "": {"handlers": ["console"], "level": env.str("LOG_LEVEL", default="INFO")}
    },
}

# static files

STATIC_URL = "/static/"

# disable trampoline to improve performance
# see https://github.com/graphql-python/graphene/issues/268
# this means though that data loader won't work which we currently don't use
# best to remove once graphql-core-next is compatible with graphene.
async_instance.disable_trampoline()


# GraphQL
if DEBUG:
    GRAPHENE["MIDDLEWARE"].append("graphene_django.debug.DjangoDebugMiddleware")
