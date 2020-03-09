# Extension points

Caluma is meant to be used as a service with a clean API hence it doesn't provide a Django app.
For customization some clear extension points are defined. In case a customization is needed
where no extension point is defined, best [open an issue](https://github.com/projectcaluma/caluma/issues/new) for discussion.

## Visibility classes

The visibility part defines what you can see at all. Anything you cannot see, you're implicitly also not allowed to modify. The visibility classes define what you see depending on your roles, permissions, etc. Building on top of this follow the permission classes (see below) that define what you can do with the data you see.

Visibility classes are configured as `VISIBILITY_CLASSES`.

Following pre-defined classes are available:
* `caluma.caluma_core.visibilities.Any`: Allow any user without any filtering
* `caluma.caluma_core.visibilities.Union`: Union result of a list of configured visibility classes. May only be used as base class.
* `caluma.caluma_user.visibilities.Authenticated`: Only show data to authenticated users
* `caluma.caluma_user.visibilities.CreatedByGroup`: Only show data that belongs to the same group as the current user
* `caluma.caluma_workflow.visibilities.AddressedGroups`: Only show case, work item and document to addressed users through group

In case this default classes do not cover your use case, it is also possible to create your custom
visibility class defining per node how to filter.

Example:
```python
from caluma.caluma_core.visibilities import BaseVisibility, filter_queryset_for
from caluma.caluma_core.types import Node
from caluma.caluma_form.schema import Form


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
* `info`: [The `info` object](interfaces.md#the-info-object)

Save your visibility module as `visibilities.py` and inject it as Docker volume to path `/app/caluma/extensions/visibilities.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `VISIBILITY_CLASSES` as `caluma.extensions.visibilities.CustomVisibility`.

## Permission classes

Permission classes define who may perform which mutation. Such can be configured as `PERMISSION_CLASSES`.

Following pre-defined classes are available:
* `caluma.caluma_user.permissions.IsAuthenticated`: only allow authenticated users
* `caluma.caluma_core.permissions.AllowAny`: allow any users to perform any mutation.
* `caluma.caluma_user.permissions.CreatedByGroup`: Only allow mutating data that belongs to same group as current user

In case this default classes do not cover your use case, it is also possible to create your custom
permission class defining per mutation and mutation object what is allowed.

Example:
```python
from caluma.caluma_core.permissions import BasePermission, permission_for, object_permission_for
from caluma.caluma_form.schema import SaveForm
from caluma.caluma_core.mutation import Mutation


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
* `info`: [The `info` object](interfaces.md#the-info-object)
* `instance`: instance being edited by specific mutation

Save your permission module as `permissions.py` and inject it as Docker volume to path `/app/caluma/extensions/permissions.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `PERMISSION_CLASSES` as `caluma.extensions.permissions.CustomPermission`.

If your permissions depend on the content of the mutation, you can access those
values via the `get_params()` method on the mutation, like the following
example shows:

```python
class CustomPermission(BasePermission):
    @permission_for(SaveTextQuestionInput)
    def hsa_question_save_permission(self, mutation, info):
        params = mutation.get_params(info)
        # hypothetical permission: disallow saving
        # questions whose label contains the word "blah"
        return "blah" not in params['input']['label']
```

## Validation classes

Validation classes can validate or amend input data of any mutation. Each mutation is processed in two steps:

1. Permission classes check if a given mutation is allowed based on the object being mutated, and
2. Validation classes process (and potentially amend) input data of a given mutation

A custom validation class defining validations for various mutations looks like this:

```python
from caluma.caluma_core.validations import BaseValidation, validation_for
from caluma.caluma_form.schema import SaveForm
from caluma.caluma_core.mutation import Mutation
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
* `info`: [The `info` object](interfaces.md#the-info-object)

Save your validation module as `validations.py` and inject it as Docker volume to path `/app/caluma/extensions/validations.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/master/docker-compose.yml) for an example.

Afterwards you can configure it in `VALIDATION_CLASSES` as `caluma.extensions.validations.CustomValidation`.

## FormatValidator classes

Custom FormatValidator classes can be created to validate input data for answers, based
on rules set on the question.

There are some [core FormatValidators](#formatvalidators) you can use.

A custom FormatValidator looks like this:

```python
from caluma.caluma_form.format_validators import BaseFormatValidator


class MyFormatValidator(BaseFormatValidator):
    slug = "my-slug"
    name = {"en": "english name", "de": "Deutscher Name"}
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    error_msg = {"en": "Not valid", "de": "Nicht gültig"}
```

For more complex validations, you can also additionally override the `validate()`
method. Obviously, everything that happens in there must also be implemented in the
corresponding frontend validation, if any.

## Custom data sources
For Choice- and MultipleChoiceQuestions it's sometimes necessary to populate the choices
with calculated data or data from external sources.

For this you can use the data_source extension point.

An example data_source looks like this:

 ```python
from caluma.caluma_data_source.data_sources import BaseDataSource
from caluma.caluma_data_source.utils import data_source_cache
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

### `get_data`-method
Must return an iterable. This iterable can contain strings, ints, floats
and also iterables. Those contained iterables can consist of maximally two items. The first
will be used for the option slug, the second one for it's label. If only one value is provided,
this value will also be used as label.

For the label, it's possible to use a dict with translated values.

Note: If the labels returned from`get_data()` depend on the current user's language,
you need to return a `dict` with the language code as keys instead of translating the
value yourself. Returning already translated values is not supported, as it would break
caching and validation.

### `validate_answer_value`-method

The default `validate_answer_value()`-method checks first if the value is contained in the output of `self.get_data()`. If it is, it returns the label. Else it makes a DB lookup to see if there is a `DynamicOption` with the same `document`, `question` and `slug` (that's the value). If there is at least one, it returns the label of the first one. Else it returns `False`.

If you override this method, make sure to return the label if valid, else `False`.

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

## Caluma events

For reacting upon Caluma Events, you can setup [event receivers](events.md)
