import os
import re

import environ
from django.utils.module_loading import import_string

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
    "graphene_django",
    "caluma.user.apps.DefaultConfig",
    "caluma.form.apps.DefaultConfig",
    "caluma.workflow.apps.DefaultConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",
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

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = env.str("LANGUAGE_CODE", "en")
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


# GraphQL

GRAPHENE = {
    "SCHEMA": "caluma.schema.schema",
    "MIDDLEWARE": ["caluma.user.middleware.OIDCAuthenticationMiddleware"],
}

# OpenID connect

OIDC_VERIFY_ALGORITHM = env.list("OIDC_VERIFY_ALGORITHM", default="HS256")
OIDC_CLIENT = env.str("OIDC_CLIENT", default=None)
OIDC_JWKS_ENDPOINT = env.str("OIDC_JWKS_ENDPOINT", default=None)
OIDC_SECRET_KEY = env.str("OIDC_SECRET_KEY", default=SECRET_KEY)
OIDC_VERIFY_SSL = env.bool("OIDC_VERIFY_SSL", default=True)
OIDC_VALIDATE_CLAIMS_OPTIONS = env.dict(
    "OIDC_VALIDATE_CLAIMS_OPTIONS", cast={"value": bool}, default=None
)

OIDC_GROUPS_CLAIM = env.str("OIDC_GROUPS_CLAIM", default="caluma_groups")

# Extensions

VISIBILITY_CLASSES = [
    import_string(cls)
    for cls in env.list(
        "VISIBILITY_CLASSES", default=default(["caluma.visibilities.Any"])
    )
]


PERMISSION_CLASSES = [
    import_string(cls)
    for cls in env.list(
        "PERMISSION_CLASSES", default=default(["caluma.permissions.AllowAny"])
    )
]
