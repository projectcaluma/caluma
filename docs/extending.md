# Extension points

Caluma is meant to be used as a service with a clean API hence it doesn't provide a Django app.
For customization some clear extension points are defined. In case a customization is needed
where no extension point is defined, best [open an issue](https://github.com/projectcaluma/caluma/issues/new) for discussion.

## Visibility classes

The visibility part defines what you can see at all. Anything you cannot see, you're implicitly also not allowed to modify. The visibility classes define what you see depending on your roles, permissions, etc. Building on top of this follow the permission classes (see below) that define what you can do with the data you see.

Visibility classes are configured as `VISIBILITY_CLASSES`.

Following pre-defined classes are available:

- `caluma.caluma_core.visibilities.Any`: Allow any user without any filtering
- `caluma.caluma_core.visibilities.Union`: Union result of a list of configured visibility classes. May only be used as base class.
- `caluma.caluma_user.visibilities.Authenticated`: Only show data to authenticated users
- `caluma.caluma_user.visibilities.CreatedByGroup`: Only show data that belongs to the same group as the current user
- `caluma.caluma_workflow.visibilities.AddressedGroups`: Only show case, work item and document to addressed users through group

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
        return queryset.filter(created_by_user=info.context.user.username)

    @filter_queryset_for(Form)
    def filter_queryset_for_form(self, node, queryset, info):
        return queryset.exclude(slug='protected-form')
```

Arguments:

- `node`: GraphQL node filtering queryset for
- `queryset`: [Queryset](https://docs.djangoproject.com/en/2.1/ref/models/querysets/) of specific node type
- `info`: [The `info` object](interfaces.md#the-info-object)

Save your visibility module as `visibilities.py` and inject it as Docker volume to path `/app/caluma/extensions/visibilities.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/main/docker-compose.yml) for an example.

Afterwards you can configure it in `VISIBILITY_CLASSES` as `caluma.extensions.visibilities.CustomVisibility`.

## Permission classes

Permission classes define who may perform which mutation. Such can be configured as `PERMISSION_CLASSES`.

Following pre-defined classes are available:

- `caluma.caluma_user.permissions.IsAuthenticated`: only allow authenticated users
- `caluma.caluma_core.permissions.AllowAny`: allow any users to perform any mutation.
- `caluma.caluma_user.permissions.CreatedByGroup`: Only allow mutating data that belongs to same group as current user

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

- `mutation`: mutation class
- `info`: [The `info` object](interfaces.md#the-info-object)
- `instance`: instance being edited by specific mutation

Save your permission module as `permissions.py` and inject it as Docker volume to path `/app/caluma/extensions/permissions.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/main/docker-compose.yml) for an example.

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
        if data['meta'] and 'admin' not in info.context.user.groups:
            raise exceptions.ValidationError('May not change meta on form')
        return data
```

Arguments:

- `mutation`: mutation class
- `data`: input data with resolved relationships (e.g. a form ID is represented as actual form object)
- `info`: [The `info` object](interfaces.md#the-info-object)

Save your validation module as `validations.py` and inject it as Docker volume to path `/app/caluma/extensions/validations.py`,
see [docker-compose.yml](https://github.com/projectcaluma/caluma/blob/main/docker-compose.yml) for an example.

Afterwards you can configure it in `VALIDATION_CLASSES` as `caluma.extensions.validations.CustomValidation`.

### The main group of the user

By default, Caluma assumes the first group in the list of groups it receives from the OIDC provider as the group the request was made in the name of.
This means, this group will be written into the `created_by_group` field on the records that get created during the request.

It is possible to manually set this group in the validation class, in order to override this behavior:

```python
from caluma.caluma_core.validations import BaseValidation


class CustomValidation(BaseValidation):
    def validate(self, mutation, data, info):
        # the list of groups received from the OIDC provider can be accessed with
        # info.context.user.groups
        # Overriding the main group can be achieved by setting the `group` property on the user object:
        info.context.user.group = "foobar"
        return data
```

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
   def get_data(self, user):
       response = requests.get(f"https://someapi/?user={user.username}")
       return [result["value"] for result in response.json()["results"]]
```

This class needs also to be added to the `DATA_SOURCE_CLASSES` environment variable.

### Properties

- `info`: Descriptive text for the data source (can also be a multilingual dict)
- `default`: The default value to be returned if execution of `get_data()` fails. If
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

## Dynamic Groups

Caluma allows you to extend the JEXL evaluation in the `address_groups` and `control_groups` properties of a `Task`.
The result of this evaluation ends up in the generated `WorkItem`'s `addressed_groups` and `controlling_groups` fields respectively.

A typical use-case for such "dynamic groups" would be to define role based groups.

To configure a dynamic groups class, you can set the `DYNAMIC_GROUPS_CLASSES` environment variable.
When using the Caluma service, you can place your class in `caluma.extensions.dynamic_groups` and set `DYNAMIC_GROUPS_CLASSES` to `["caluma.extensions.dynamic_groups.CustomDynamicGroups"]`.

### Example

```python
from your.project.code import find_legal_dept
from caluma.caluma_workflow.dynamic_groups import (
    BaseDynamicGroups,
    register_dynamic_group,
)


class CustomDynamicGroups(BaseDynamicGroups):
    @register_dynamic_group("legal_dept")
    def resolve_legal_dept(self, task, case, user, prev_work_item, context):
        # custom business logic which returns either a string or a list of strings
        return find_legal_dept(case)
```

You can then use that defined dynamic group `"legal_dept"` in the `Task` properties by postfixing them with a transform: `"legal_dept"|groups`.
The created `WorkItem` would then have an evaluated value like `["legal-dept-boston"]` or `["legal-dept-nyc"]` for that property.

The `context` can hold an arbitrary dict passed in the `context` variable in a `SaveCase` or `CompleteWorkItem` mutation.
Use it for passing additional info and implement logic on it, for example run-time dependent `"addressed_groups"` that should be added to newly generated `WorkItems`.

We can extend our example above:

```python
class CustomDynamicGroups(BaseDynamicGroups):
    @register_dynamic_group("legal_dept")
    def resolve_legal_dept(self, task, case, user, prev_work_item, context):
        # context may contain arbitrary data from the client to affect behaviour...
        legal_depts = find_legal_dept(case, coast=context.get("coast"))

        # ... or plain groups to include
        return legal_depts + context.get("additional_groups", [])
```

Now if the `context` looks like `{"coast": "west", "additional_groups": ["board", "administration"]}`, the resulting groups are `["legal-dept-san-francisco", "legal-dept-seattle", "board", "administration"]`.

## Dynamic Tasks

Caluma allows you to extend the JEXL evaluation in the `next` property of a
flow. This `next` property decides which task(s) will be started on
completing or skipping a work item.

This concept can be used to implement an exclusive choice flow. E.g if the
document of the case has a certain answer it will start a different task than
normally.

To configure a dynamic tasks class, you can set the `DYNAMIC_TASKS_CLASSES` environment variable.
When using the Caluma service, you can place your class in `caluma.extensions.dynamic_tasks` and set `DYNAMIC_TASKS_CLASSES` to `["caluma.extensions.dynamic_tasks.CustomDynamicTasks"]`.

### Example

```python
from caluma.caluma_workflow.dynamic_tasks import (
    BaseDynamicTasks,
    register_dynamic_task,
)


class CustomDynamicTasks(BaseDynamicTasks):
    @register_dynamic_task("audit-forms")
    def resolve_audit_forms(self, case, user, prev_work_item, context):
        needs_extra_audit = case.document.answers.filter(
            question_id="is-extra-complicated",
            value="is-extra-complicated-yes"
        ).exists()
        next_tasks = ["audit"]

        if needs_extra_audit:
            next_tasks.append("extra-audit")

        return next_tasks
```

You can then use that defined dynamic task `"audit-forms"` in the `next`
property by postfixing it with a `task` or `tasks` transform:
`["audit-forms"]|tasks`. Please keep in mind that if you use the singular
`task` transform, the dynamic task method can only return a single task or it
will raise an exception.

## Caluma events

For reacting upon Caluma Events, you can setup [event receivers](events.md)

## OIDC User factory

Especially when using Caluma embedded in another Django project, you need to
ensure compatibility with other components. Caluma does not represent users
as a database object, but instead uses a "shim" object in it's role as an OIDC
relying party (RP) that represents the requesting user.
Oher projects may have differing requirements however.

Therefore, you can define a custom `CALUMA_OIDC_USER_FACTORY`. The setting is a string
that points to a callable, which is expected to return an OIDC user object.
By default it points to `caluma.caluma_user.models.OIDCUser`.

The factory needs to provide the following interface:

```python
    def user_factory(token, userinfo=None, introspection=None):
        # Either `userinfo` or `introspection` is filled with a dict
        # with information about the user.
        return SomeOIDCUserObject(...)
```

The resulting object is expected to provide the following properties:
* `username` - returns the username.
* `group` - The primary group of the user. Used to fill in `created_by_group` etc
* `is_authenticated` - Boolean, should always be `True`

You may extend the object as you please, for example by providing
shortcuts to data you need often  (reference to a Django user model if
you use one, etc).
