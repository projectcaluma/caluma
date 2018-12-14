# Caluma Service

[![Build Status](https://travis-ci.com/projectcaluma/caluma.svg?branch=master)](https://travis-ci.org/projectcaluma/caluma)
[![Codecov](https://codecov.io/gh/projectcaluma/caluma/branch/master/graph/badge.svg)](https://codecov.io/gh/projectcaluma/caluma)
[![Pyup](https://pyup.io/repos/github/projectcaluma/caluma/shield.svg)](https://pyup.io/account/repos/github/projectcaluma/caluma/)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/projectcaluma/caluma)
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

**Question** defines a single input of a form, such as a text input, checkbox or similar. Each question type has a specific representation and validation.

**Document** is a specific instance of a form. Since a form is a collection of questions, a document can be thought of as a collection of answers.

**Answer** contains user input answering a question. There are different answer representations covering different data types.

#### Workflow entities

The naming and concept of workflow entities is inspired by the [Workflow Patterns Initiative](http://www.workflowpatterns.com/).

**Workflow** defines the structure of a business process. It is built up of tasks which are connected by forward-referencing flows.

**Task** is a single action that occurs in a business process.

**Flow** defines the ordering and dependencies between tasks.

**Case** is a specific instance of a workflow. It has an internal state which represents it's progress.

**WorkItem** is a single unit of work that needs to be completed in a specific stage of a case.

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

#### Authentication and authorization

If you want connect Caluma you need a [IAM](https://en.wikipedia.org/wiki/Identity_management) supporting OpenID Connect. If not available you might want to consider using [Keycloak](https://www.keycloak.org/).

* `OIDC_VERIFY_ALGORITHM`: Token verification algorithm (default: HS256)
* `OIDC_CLIENT`: Client name
* `OIDC_JWKS_ENDPOINT`: End point of JWKS in case a asymentric algorithm is used.
* `OIDC_SECRET_KEY`: Secret key when symmetric algorithm is used (defaults to `SECRET_KEY`)
* `OIDC_VALIDATE_CLAIMS_OPTIONS` dict of verify signature options. See [options parameter](https://python-jose.readthedocs.io/en/latest/jwt/api.html?highlight=decode_token#jose.jwt.decode) for details.
* `OIDC_GROUPS_CLAIM`: Name of claim to be used to represent groups (default: caluma_groups)

#### Extension points

Caluma is meant to be used as a service with a clean API hence it doesn't provide a Django app.
For customization some clear extension points are defined. In case a customization is needed
where no extension point is defined, best [open an issue](https://github.com/projectcaluma/caluma/issues/new) for discussion.

##### Visibility classes

The visibility part defines what you can see at all. Anything you cannot see, you're implicitly also not allowed to modify. The visibility classes define what you see depending on your roles, permissions, etc. Building on top of this follow the permission classes (see below) that define what you can do with the data you see.

Visibility classes are configured as `VISIBILITY_CLASSES`.

Following pre-defined classes are available:
* `caluma.core.visibilities.Any`: Allow any user without any filtering
* `caluma.user.visibilities.Authenticated`: Only show data to authenticated users
* `caluma.user.visibilities.CreatedByGroup`: Only show data that belongs to the same group as the current user

In case this default classes do not cover your use case, it is also possible to create your custom
visibility class defining per node how to filter.

Example:
```python
from caluma.types import Node
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
* `info`: Resolver info, whereas `info.context` is the [http request](https://docs.djangoproject.com/en/2.1/ref/request-response/#httprequest-objects) and user can be accessed through `info.context.user`

Save your visibility module as `visibility.py` and inject it as Docker volume to path `/app/caluma/extensions/visibility.py`,
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
from caluma.form.schema import SaveForm
from caluma.mutation import Mutation

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
* `info`: resolver info, whereas `info.context` is the [http request](https://docs.djangoproject.com/en/2.1/ref/request-response/#httprequest-objects) and user can be accessed through `info.context.user`
* `instance`: instance being edited by specific mutation

Save your permission module as `permissions.py` and inject it as Docker volume to path `/app/caluma/extensions/permissions.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `PERMISSION_CLASSES` as `caluma.extensions.permissions.CustomPermission`.

## Contributing

Look at our [contributing guidelines](CONTRIBUTION.md) to start with your first contribution.

## License
Code released under the [MIT license](LICENSE).
