"""
This settings module only contains caluma specific settings.

It's imported by the main caluma settings and is intended to also be used by third party
applications integrating Caluma.
"""


import os

import environ

env = environ.Env()
django_root = environ.Path(__file__) - 3

ENV_FILE = env.str("ENV_FILE", default=django_root(".env"))
if os.path.exists(ENV_FILE):  # pragma: no cover
    environ.Env.read_env(ENV_FILE)

# per default production is enabled for security reasons
# for development create .env file with ENV=development
ENV = env.str("ENV", "production")


def default(default_dev=env.NOTSET, default_prod=env.NOTSET):
    """Environment aware default."""
    return default_prod if ENV == "production" else default_dev


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
MINIO_PRESIGNED_TTL_MINUTES = env.int("MINIO_PRESIGNED_TTL_MINUTES", default=15)
MINIO_DISABLE_CERT_CHECKS = env.bool("MINIO_DISABLE_CERT_CHECKS", default=False)


# GraphQL

GRAPHENE = {
    "SCHEMA": "caluma.schema.schema",
    "MIDDLEWARE": [],
    "RELAY_CONNECTION_MAX_LIMIT": None,
}

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

CALUMA_OIDC_USER_FACTORY = env.str(
    "CALUMA_OIDC_USER_FACTORY", default="caluma.caluma_user.models.OIDCUser"
)


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

EVENT_RECEIVER_MODULES = env.list("EVENT_RECEIVER_MODULES", default=[])

DYNAMIC_GROUPS_CLASSES = env.list("DYNAMIC_GROUPS_CLASSES", default=[])

DYNAMIC_TASKS_CLASSES = env.list("DYNAMIC_TASKS_CLASSES", default=[])

# simple history
SIMPLE_HISTORY_HISTORY_ID_USE_UUID = True

# Historical API
ENABLE_HISTORICAL_API = env.bool("ENABLE_HISTORICAL_API", default=False)

# Configure the fields you intend to use in the "meta" fields. This will
# provide corresponding constants in the ordreBy filter, as well as allow
# you to use those fields in the analytics module.
META_FIELDS = env.list("META_FIELDS", default=[])

# enable caluma healthz endpoint
ENABLE_HEALTHZ_ENDPOINT = env.bool("ENABLE_HEALTHZ_ENDPOINT", default=False)
