# Configuration

Caluma is a [12factor app](https://12factor.net/) which means that configuration is stored in environment variables.
Different environment variable types are explained at [django-environ](https://github.com/joke2k/django-environ#supported-types).

## Common

A list of configuration options which you might need to configure to get Caluma started in your environment.

* `UID`: The user ID used in the container
* `SECRET_KEY`: A secret key used for cryptography. This needs to be a random string of a certain length. See [more](https://docs.djangoproject.com/en/2.1/ref/settings/#std:setting-SECRET_KEY).
* `ALLOWED_HOSTS`: A list of hosts/domains your service will be served from. See [more](https://docs.djangoproject.com/en/2.1/ref/settings/#allowed-hosts).
* `DATABASE_HOST`: Host to use when connecting to database (default: localhost)
* `DATABASE_PORT`: Port to use when connecting to database (default: 5432)
* `DATABASE_NAME`: Name of database to use (default: caluma)
* `DATABASE_USER`: Username to use when connecting to the database (default: caluma)
* `DATABASE_PASSWORD`: Password to use when connecting to database
* `LANGUAGE_CODE`: Default language defined as fallback (default: en)
* `LANGUAGES`: List of supported language codes (default: all available)
* `LOG_LEVEL`: [Log level](https://docs.djangoproject.com/en/1.11/topics/logging/#loggers) of messages to write to output (default: INFO)

## Authentication and authorization

If you want to connect to Caluma you need an
[IAM](https://en.wikipedia.org/wiki/Identity_management) supporting
OpenID Connect. If you don't have this available in your environment already,
you might want to consider using [Keycloak](https://www.keycloak.org/).

Caluma expects a bearer token to be passed on as [Authorization Request Header Field](https://tools.ietf.org/html/rfc6750#section-2.1)

* `OIDC_USERINFO_ENDPOINT`: Url of userinfo endpoint as [described](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo)
* `OIDC_GROUPS_CLAIM`: Name of claim to be used to represent groups (default: caluma_groups)
* `OIDC_USERNAME_CLAIM`: Name of claim to be used to represent the username (default: sub)
* `OIDC_BEARER_TOKEN_REVALIDATION_TIME`: Time in seconds before bearer token validity is verified again. For best security token is validated on each request per default. It might be helpful though in case of slow Open ID Connect provider to cache it. It uses [cache](#cache) mechanism for memorizing userinfo result. Number has to be lower than access token expiration time. (default: 0)

## Cache

* `CACHE_BACKEND`: [cache backend](https://docs.djangoproject.com/en/1.11/ref/settings/#backend) to use (default: django.core.cache.backends.locmem.LocMemCache)
* `CACHE_LOCATION`: [location](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-CACHES-LOCATION) of cache to use

## CORS headers

Per default no CORS headers are set but can be configured with following options.

* `CORS_ORIGIN_ALLOW_ALL`: If True, the whitelist will not be used and all origins will be accepted. (default: False)
* `CORS_ORIGIN_WHITELIST`: A list of origin hostnames (including the scheme and with optional port) that are authorized to make cross-site HTTP requests.

## Historical API
If you wish to expose an API for querying previous revisions of documents, you need to set following environment variable:

`ENABLE_HISTORICAL_API`: Defaults to `false`.

If you enable this, make sure to also configure [visibilities](extending.md#visibility-classes) and
[permissions](extending.md#permission-classes) for historical types.

## Access Logging

The `caluma_logging` app bundles a middleware that logs all requests using the `AccessLog` model.
The log entries consist of username and caluma query/mutation details.

It's enabled by setting the environment variable:
`ENABLE_ACCESS_LOG`: Defaults to `false`.

For cleaning up old entries it's encouraged to use the `cleanup_access_log` management command.
Given the `--force` argument, it removes all entries older than what's given by `--keep` (default: "2 weeks").

## File question and answers
In order to make use of Calumas file question and answer, you need to set up a storage provider.

For the time being, only [MinIO](https://min.io/) is supported. Other providers may follow.

In the [docker-compose.yml](../docker-compose.yml)
you can find an example configuration for a MinIO container.

The following environment variables need to be set for caluma to use MinIO:

* `MEDIA_STORAGE_SERVICE`: defaults to "minio" (this is the only supported type
   at this time)
* `MINIO_STORAGE_ENDPOINT`: defaults to "minio:9000"
* `MINIO_STORAGE_ACCESS_KEY`: defaults to "minio"
* `MINIO_STORAGE_SECRET_KEY`: defaults to "minio123"
* `MINIO_STORAGE_USE_HTTPS`: defaults to False
* `MINIO_STORAGE_MEDIA_BUCKET_NAME`: defaults to "caluma-media"
* `MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET`: defaults to True
* `MINIO_PRESIGNED_TTL_MINUTES`: defaults to 15

Caluma only handles metadata about files, not the files itself. When saving a `FileAnswer`, Caluma
will return a presigned `uploadUrl`, which the client can use to upload the file directly to the storage provider.

The same goes for retrieving files. Caluma will respond with a presigned `downloadUrl` for
the client to directly download the file from the storage provider.

In case you run HTTPS in your local development environment, you might have a
self-signed certificate. The Minio client by default verifies the TLS
certificates, so would fail in this case. You can set `MINIO_DISABLE_CERT_CHECKS`
to `true` to avoid this. Note: This setting only works if you also set `DEBUG`
to `true` as well.

## Client tokens
If you want to use additional services that need to talk to caluma (e.g.
[caluma-interval](https://github.com/projectcaluma/caluma-interval)), you need to have
an additional OIDC-client with the `token_introspection` scope key.

Following environment variables need to be set for caluma:

* `OIDC_INTROSPECT_ENDPOINT`: introspect endpoint from the OIDC-provider
* `OIDC_INTROSPECT_CLIENT_ID`: ID of the OIDC-client
* `OIDC_INTROSPECT_CLIENT_SECRET`: Secret of the OIDC-client

Some OIDC implementations (e.g. keycloak), allow for querying the `userinfo` endpoint
with a client token. In that case the `introspection` endpoint is never called.

The attribute `claims_source` on `OIDCUser` instances indicates the source of the claims.


## uWSGI defaults

We are using the sane uWSGI-defaults researched by [bloomberg](https://www.techatbloomberg.com/blog/configuring-uwsgi-production-deployment/?sf104898833=1). You can override the defaults using environment variables.

- `UWSGI_STRICT`=`true`
- `UWSGI_WSGI_FILE`=`/app/caluma/wsgi.py`
- `UWSGI_MASTER`=`true`
- `UWSGI_ENABLE_THREADS`=`true`
- `UWSGI_VACUUM`=`true`
- `UWSGI_SINGLE_INTERPRETER`=`true`
- `UWSGI_DIE_ON_TERM`=`true`
- `UWSGI_NEED_APP`=`true`
- `UWSGI_DISABLE_LOGGING`=`true`
- `UWSGI_LOG_4XX`=`true`
- `UWSGI_LOG_5XX`=`true`
- `UWSGI_MAX_REQUESTS`=`1000`
- `UWSGI_MAX_WORKER_LIFETIME`=`3600`
- `UWSGI_RELOAD_ON_RSS`=`2048`
- `UWSGI_WORKER_RELOAD_MERCY`=`60`
- `UWSGI_CHEAPER_ALGO`=`busyness`
- `UWSGI_PROCESSES`=`500`
- `UWSGI_CHEAPER`=`8`
- `UWSGI_CHEAPER_INITIAL`=`16`
- `UWSGI_CHEAPER_OVERLOAD`=`1`
- `UWSGI_CHEAPER_STEP`=`16`
- `UWSGI_CHEAPER_BUSYNESS_MULTIPLIER`=`30`
- `UWSGI_CHEAPER_BUSYNESS_MIN`=`20`
- `UWSGI_CHEAPER_BUSYNESS_MAX`=`70`
- `UWSGI_CHEAPER_BUSYNESS_BACKLOG_ALERT`=`16`
- `UWSGI_CHEAPER_BUSYNESS_BACKLOG_STEP`=`2`
- `UWSGI_HARAKIRI`=`60`
- `UWSGI_AUTO_PROCNAME`=`true`
- `UWSGI_PROCNAME_PREFIX`=`"caluma "`

See https://git.io/JemA2 for more information.
