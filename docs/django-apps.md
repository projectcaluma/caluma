# Using Caluma as django apps

## Disclaimer

It is highly recommended to use Caluma as a dedicated service. However, there are usecases, where
it might make sense to integrate Caluma into another django project.

If you just want to get Caluma up and running, please see the documentation about [setting up
the Caluma service](configuration.md).

Please beware that Caluma only works with PostgreSQL, and requires the `psqlextra`
backend to use the advanced features (such as JSON fields etc).

## Installation

Caluma is on PyPI, so you can just

```shell
pip install caluma
```


## Configuration

### Installed apps

Add the Caluma apps you want to use to your `INSTALLED_APPS`.

Some notes about Caluma-internal dependencies:

* `caluma_core` should always be added when using Caluma
* `caluma_user` should always be added when using Caluma
* `caluma_workflow` needs `caluma_form` to work correctly (as cases and work items point to documents)

```python
INSTALLED_APPS = [
    # ...
    # Caluma and it's dependencies:
    "caluma.caluma_core.apps.DefaultConfig",
    "caluma.caluma_user.apps.DefaultConfig",
    "caluma.caluma_form.apps.DefaultConfig",
    "caluma.caluma_workflow.apps.DefaultConfig",
    "caluma.caluma_data_source.apps.DefaultConfig",
    "graphene_django",
    "localized_fields",
    "psqlextra",  # Caluma needs a PostgreSQL database using the psqlextra backend
    "simple_history",
    # ...
]
```

### Settings

Import the Caluma settings at the top of your `DJANGO_SETTINGS_MODULE`:

```python
from caluma.settings.caluma import *  # noqa
```

This will only load Caluma specific settings and no django specific ones (db, cache, etc.).

Then you can configure caluma normally [using environment variables](configuration.md).


### Database

Caluma needs a PostgreSQL database using the `psqlextra` backend to use the advanced
features (such as JSON fields etc).

This is mandatory, that's why we tell you thrice.

### Debug middleware

It's recommended to add following lines to your settings file (after importing the caluma settings):

```python
# GraphQL
if DEBUG:
    GRAPHENE["MIDDLEWARE"].append("graphene_django.debug.DjangoDebugMiddleware")
```


### urls.py

Include the Caluma URLs (this example uses `graphql` as URL prefix):

```python
from django.conf.urls import include, url

urlpatterns = [
    # ...
    url(r"^graphql", include("caluma.caluma_core.urls")),
    # ...
]
```


## Supported interfaces

See [interfaces](interfaces.md) for information about the officially supported API.

