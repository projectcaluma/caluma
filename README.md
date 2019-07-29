# ![Caluma Service](https://user-images.githubusercontent.com/6150577/60805422-51b1bf80-a180-11e9-9ae5-c794249c7a98.png)

[![Build Status](https://travis-ci.com/projectcaluma/caluma.svg?branch=master)](https://travis-ci.com/projectcaluma/caluma)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/projectcaluma/caluma/blob/master/.coveragerc#L5)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A collaborative form editing service.

## What is Caluma Service?

Caluma Service is the core part of the Caluma project providing a [GraphQL API](https://graphql.org/). For a big picture have a look at [caluma.io](https://caluma.io)

## Getting started

### Installation

**Requirements**
* docker
* docker-compose

After installing and configuring those, download [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) and run the following command:


```bash
docker-compose up -d
```

You can now access [GraphiQL](https://github.com/graphql/graphiql) at [http://localhost:8000/graphql](http://localhost:8000/graphql) which includes a schema documentation. The API allows to
query and mutate form and workflow entities which are described below.

### Entities

Caluma is split in two parts, form and workflow. The form can be used without a workflow and vice versa, but the full power of Caluma comes when combining the two.

Each part is based on several entities, which usually come in pairs: One defines a "blueprint" and is instance-independent, while the other one represents the blueprint in relation to a specific instance. The two entities are usually connected by a one-to-many relationship, e.g. there can be many concrete `cases` (instance-specific) following a certain `workflow` (global blueprint).

#### Form entities

**Form** defines the structure of a document, basically a collection of questions.

**Question** defines a single input of a form, such as a text, choice or similar. Each question type has a specific representation and validation.

**Document** is a specific instance of a form. Since a form is a collection of questions, a document can be thought of as a collection of answers.

**Answer** contains user input answering a question. There are different answer representations covering different data types.

#### Workflow entities

The naming and concept of workflow entities is inspired by the [Workflow Patterns Initiative](http://www.workflowpatterns.com/).

**Workflow** defines the structure of a business process. It is built up of tasks which are connected by forward-referencing flows.

**Task** is a single action that occurs in a business process.

**Flow** defines the ordering and dependencies between tasks.

**Case** is a specific instance of a workflow. It has an internal state which represents it's progress.

**WorkItem** is a single unit of work that needs to be completed in a specific stage of a case.

#### User entities

User entities are not actual entities on Caluma but provided through authentication token of an OpenID connect provider (see configuration below).

**User** is a human resource which can be part of one or several groups.

**Group** is a collection of users typically a organization.

### Technical components

#### Javascript Expression Language

Caluma relies on Javascript Expression Language alias [JEXL](https://github.com/TomFrost/Jexl) for defining powerful yet simple expressions for complex validation and flow definitions.
Reason for using JEXL over other languages is that it can be simply introspected in the backend and frontend as of its defined small scope.

### Configuration

Caluma is a [12factor app](https://12factor.net/) which means that configuration is stored in environment variables.
Different environment variable types are explained at [django-environ](https://github.com/joke2k/django-environ#supported-types).

#### Common

A list of configuration options which you might need to configure to get Caluma started in your environment.

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

#### Authentication and authorization

If you want to connect to Caluma you need an [IAM](https://en.wikipedia.org/wiki/Identity_management) supporting OpenID Connect. If not available you might want to consider using [Keycloak](https://www.keycloak.org/).

Caluma expects a bearer token to be passed on as [Authorization Request Header Field](https://tools.ietf.org/html/rfc6750#section-2.1)

* `OIDC_USERINFO_ENDPOINT`: Url of userinfo endpoint as [described](https://openid.net/specs/openid-connect-core-1_0.html#UserInfo)
* `OIDC_GROUPS_CLAIM`: Name of claim to be used to represent groups (default: caluma_groups)
* `OIDC_BEARER_TOKEN_REVALIDATION_TIME`: Time in seconds before bearer token validity is verified again. For best security token is validated on each request per default. It might be helpful though in case of slow Open ID Connect provider to cache it. It uses [cache](#cache) mechanism for memorizing userinfo result. Number has to be lower than access token expiration time. (default: 0)

#### Cache

* `CACHE_BACKEND`: [cache backend](https://docs.djangoproject.com/en/1.11/ref/settings/#backend) to use (default: django.core.cache.backends.locmem.LocMemCache)
* `CACHE_LOCATION`: [location](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-CACHES-LOCATION) of cache to use

#### CORS headers

Per default no CORS headers are set but can be configured with following options.

* `CORS_ORIGIN_ALLOW_ALL`: If True, the whitelist will not be used and all origins will be accepted. (default: False)
* `CORS_ORIGIN_WHITELIST`: A list of origin hostnames (including the scheme and with optional port) that are authorized to make cross-site HTTP requests.

#### FormatValidators
FormatValidator classes can validate input data for answers, based on rules set on the question.

There are a variety of base FormatValidators ready to use. There is also an [extension point](#formatvalidator-classes) for them.

List of built-in base FormatValidators:

* email
* phone-number

#### Extension points

Caluma is meant to be used as a service with a clean API hence it doesn't provide a Django app.
For customization some clear extension points are defined. In case a customization is needed
where no extension point is defined, best [open an issue](https://github.com/projectcaluma/caluma/issues/new) for discussion.

##### Visibility classes

The visibility part defines what you can see at all. Anything you cannot see, you're implicitly also not allowed to modify. The visibility classes define what you see depending on your roles, permissions, etc. Building on top of this follow the permission classes (see below) that define what you can do with the data you see.

Visibility classes are configured as `VISIBILITY_CLASSES`.

Following pre-defined classes are available:
* `caluma.core.visibilities.Any`: Allow any user without any filtering
* `caluma.core.visibilities.Union`: Union result of a list of configured visibility classes. May only be used as base class.
* `caluma.user.visibilities.Authenticated`: Only show data to authenticated users
* `caluma.user.visibilities.CreatedByGroup`: Only show data that belongs to the same group as the current user
* `caluma.workflow.visibilities.AddressedGroups`: Only show case, work item and document to addressed users through group

In case this default classes do not cover your use case, it is also possible to create your custom
visibility class defining per node how to filter.

Example:
```python
from caluma.core.visibilities import BaseVisibility, filter_queryset_for
from caluma.core.types import Node
from caluma.form.schema import Form


class CustomVisibility(BaseVisibility):
    @filter_queryset_for(Node)
    def filter_queryset_for_all(self, node, queryset, info):
        return queryset.filter(created_by_user=info.context.request.user.username)

    @filter_queryset_for(Form)
    def filter_queryset_for_form(self, node, queryset, info):
        return queryset.exclude(slug='protected-form')
```

Arguments:
* `node`: GraphQL node filtering queryset for
* `queryset`: [Queryset](https://docs.djangoproject.com/en/2.1/ref/models/querysets/) of specific node type
* `info`: Resolver info, whereas `info.context` is the [http request](https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects) and user can be accessed through `info.context.user`

Save your visibility module as `visibilities.py` and inject it as Docker volume to path `/app/caluma/extensions/visibilities.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `VISIBILITY_CLASSES` as `caluma.extensions.visibilities.CustomVisibility`.

##### Permission classes

Permission classes define who may perform which mutation. Such can be configured as `PERMISSION_CLASSES`.

Following pre-defined classes are available:
* `caluma.user.permissions.IsAuthenticated`: only allow authenticated users
* `caluma.core.permissions.AllowAny`: allow any users to perform any mutation.
* `caluma.user.permissions.CreatedByGroup`: Only allow mutating data that belongs to same group as current user

In case this default classes do not cover your use case, it is also possible to create your custom
permission class defining per mutation and mutation object what is allowed.

Example:
```python
from caluma.core.permissions import BasePermission, permission_for, object_permission_for
from caluma.form.schema import SaveForm
from caluma.core.mutation import Mutation


class CustomPermission(BasePermission):
    @permission_for(Mutation)
    def has_permission_default(self, mutation, info):
        # change default permission to False when no more specific
        # permission is defined.
        return False

    @permission_for(SaveForm)
    def has_permission_for_save_form(self, mutation, info):
        return True

    @object_permission_for(SaveForm)
    def has_object_permission_for_save_form(self, mutation, info, instance):
        return instance.slug != 'protected-form'
```

Arguments:
* `mutation`: mutation class
* `info`: resolver info, whereas `info.context` is the [http request](https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects) and user can be accessed through `info.context.user`
* `instance`: instance being edited by specific mutation

Save your permission module as `permissions.py` and inject it as Docker volume to path `/app/caluma/extensions/permissions.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `PERMISSION_CLASSES` as `caluma.extensions.permissions.CustomPermission`.

##### Validation classes

Validation classes can validate or amend input data of any mutation. Each mutation is processed in two steps:

1. Permission classes check if a given mutation is allowed based on the object being mutated, and
2. Validation classes process (and potentially amend) input data of a given mutation

A custom validation class defining validations for various mutations looks like this:

```python
from caluma.core.validations import BaseValidation, validation_for
from caluma.form.schema import SaveForm
from caluma.core.mutation import Mutation
from rest_framework import exceptions


class CustomValidation(BaseValidation):
    @validation_for(Mutation)
    def validate_mutation(self, mutation, data, info):
        # add your default specific validation code here
        return data

    @validation_for(SaveForm)
    def validate_save_form(self, mutation, data, info):
        if data['meta'] and info.context.group != 'admin':
            raise exceptions.ValidationError('May not change meta on form')
        return data
```

Arguments:
* `mutation`: mutation class
* `data`: input data with resolved relationships (e.g. a form ID is represented as actual form object)
* `info`: resolver info, whereas `info.context` is the [http request](https://docs.djangoproject.com/en/1.11/ref/request-response/#httprequest-objects) and user can be accessed through `info.context.user`

Save your validation module as `validations.py` and inject it as Docker volume to path `/app/caluma/extensions/validations.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `VALIDATION_CLASSES` as `caluma.extensions.validations.CustomValidation`.

##### FormatValidator classes

Custom FormatValidator classes can be created to validate input data for answers, based
on rules set on the question.

There are some [core FormatValidators](#formatvalidators) you can use.

A custom FormatValidator looks like this:

```python
from caluma.form.format_validators import BaseFormatValidator


class MyFormatValidator(BaseFormatValidator):
    slug = "my-slug"
    name = {"en": "english name", "de": "Deutscher Name"}
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    error_msg = {"en": "Not valid", "de": "Nicht gültig"}
```

For more complex validations, you can also additionally override the `validate()`
method. Obviously, everything that happens in there must also be implemented in the
corresponding frontend validation, if any.


## File question and answers
In order to make use of Calumas file question and answer, you need to set up a storage provider.

For the time being, only [MinIO](https://min.io/) is supported. Other providers may follow.

In the [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml)
you can find an example configuration for a MinIO container.

Following environment variables need to be set for caluma:

* `MEDIA_STORAGE_SERVICE`: defaults to "minio" (this is the only supported atm)
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

## Custom data sources
For Choice- and MultipleChoiceQuestions it's sometimes necessary to populate the choices
with calculated data or data from external sources.

For this you can use the data_source extension point.

An example data_source looks like this:

 ```python
from caluma.data_source.data_sources import BaseDataSource
from caluma.data_source.utils import data_source_cache
import requests

class CustomDataSource(BaseDataSource):
    info = 'User choices from "someapi"'

    @data_source_cache(timeout=3600)
    def get_data(self, info):
        response = requests.get(
            f"https://someapi/?user={info.context.user.username}"
        )
        return [result["value"] for result in response.json()["results"]]
```

This class needs also to be added to the `DATA_SOURCE_CLASSES` environment variable.

### Properties

* `info`: Descriptive text for the data source (can also be a multilingual dict)
* `default`: The default value to be returned if execution of `get_data()` fails. If
             this is `None`, the Exception won't be handled. Defaults to None.
* `validate`: boolean that indicates if answers should be validated against the
              current response from `get_data()`. Defaults to `True`.

### `get_data`-method
Must return an iterable. This iterable can contain strings, ints, floats
and also iterables. Those contained iterables can consist of maximally two items. The first
will be used for the option slug, the second one for it's label. If only one value is provided,
this value will also be used as label.

For the label, it's possible to use a dict with translated values.

### `data_source_cache` decorator
This decorator allows for caching the data based on the DataSource name.

Django's cache framework is used, so you can also implement your own caching logic. When
doing so, it is advisable to use the `data_source_` prefix for the key in order to avoid
conflicts.

#### Some valid examples

```python
['my-option', {"en": "english description", "de": "deutsche Beschreibung"}, ...]

[['my-option', "my description"], ...]

['my-option', ...]

[['my-option'], ...]
```


## Client tokens
If you want to use additional services that need to talk to caluma (e.g.
[caluma-interval](https://github.com/projectcaluma/caluma-interval)), you need to have
an additional OIDC-client with the `token_introspection` scope key.

Following environment variables need to be set for caluma:

* `OIDC_INTROSPECT_ENDPOINT`: introspect endpoint from the OIDC-provider
* `OIDC_INTROSPECT_CLIENT_ID`: ID of the OIDC-client
* `OIDC_INTROSPECT_CLIENT_SECRET`: Secret of the OIDC-client

## Auditing

Caluma uses [django-simple-history](https://github.com/treyhunner/django-simple-history)
to save a history of changes to the models.

## Debugging

Set environment variable `ENV` to `dev` to enable debugging capabilities. Don't use this in production as it exposes confidential information!

This enables [Django Debug Middleware](https://docs.graphene-python.org/projects/django/en/latest/debug/).

For profiling you can use `./manage.py runprofileserver`. See [docker-compose.override.yml](docker-compose.override.yml) for
an example.

## Contributing

Look at our [contributing guidelines](CONTRIBUTING.md) to start with your first contribution.

## License
Code released under the [MIT license](LICENSE).
