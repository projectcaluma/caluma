# Healthz Endpoint

The `healthz` endpoint provides information about the health status of the 
caluma backend. This allows systems, such as Kubernetes, to monitor and perform 
readiness checks on caluma.

Please note that when you enable it, make sure it is not reachable from the
outside (proxy configuration!). Due to it's nature, it takes some resources to
check everything, which makes it prone to abuse (denial of service, DoS).

It's enabled by setting the environment variable:
`ENABLE_HEALTHZ_ENDPOINT`: Defaults to `false`.

If enabled, the endpoint is accessible through the `/healthz/` path. When 
running a development server the health status can therefore be accessed at 
[localhost:8000/healthz/](http://localhost:8000/healthz/).

The `healthz` endpoint is based on and extends the 
[django-watchman](https://github.com/mwarkentin/django-watchman) package. 

## Response

The endpoint will return a JSON response listing the performed health checks 
and their status. If all checks passed, it returns with a `200 OK` HTTP 
response status code, otherwise with a `503 Service Unavailable` response 
status. The response is a modified version of the 
[django-watchman](https://github.com/mwarkentin/django-watchman) status view.
In case of health check failures, the response doesn't contain any specific
error message or stacktrace due to security concerns.

An example response of a failed health check is shown below, which returns 
with a `503 Service Unavailable` status code:

```json
{
  "media storage service": {
    "ok": false
  },
  "caches": [
    {
      "default": {
        "ok": true
      }
    }
  ],
  "database migrations": [
    {
      "default": {
        "ok": true
      }
    }
  ],
  "databases": [
    {
      "default": {
        "ok": true
      }
    }
  ],
  "database models": [
    {
      "default": {
        "ok": true
      }
    }
  ]
}
```

## Checks

The `healthz` endpoint performs a number of health checks using the 
[django-watchman](https://github.com/mwarkentin/django-watchman) package 
extended by custom checks.

The following health checks are performed by django-watchman:
* Databases:
Verifies the connection to each database specified in the settings. If a 
connection failure is detected, the check for that particular database fails. 
The status of each checked database is listed.

* Caches:
Performs a set, get and delete operation on each of the caches specified in 
the settings. If one of the operations fail, the check for that particular
cache fails. The status of each checked cache is listed.

The following health checks were added to complement the django-watchman checks:
* Database Models:
For each database, the check tries to instantiate a model and perform retrieve, 
update and delete operations on the created model object. If one of the
operations fail, the check fails for that particular database. The status of 
the models check of each database is listed.

* Database Migrations:
Checks whether unapplied migrations are detected for any of the databases. In 
case unapplied migrations are detected, the check fails for that particular
database. The status of the migrations check of each database is listed.

* Media Storage Service:
If a media storage service is configured for storage, it tries to create an
object and perform stat, upload and download operations on the object. If one
of the operations fail, the check fails. If no media storage service is
configured, the check passes with:
`"media storage service (not configured)": {"ok": True}`.