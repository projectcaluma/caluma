import inspect
from functools import wraps

from .mutation import Mutation


def permission_for(mutation):
    """Decorate function to overwriting permission of specific mutation."""

    def decorate(fn):
        @wraps(fn)
        def _decorated(self, mutation, info):
            return fn(self, mutation, info)

        _decorated._permission = mutation
        return _decorated

    return decorate


def object_permission_for(mutation):
    """Decorate function to overwriting object permission of specific mutation."""

    def decorate(fn):
        @wraps(fn)
        def _decorated(self, mutation, info, instance):
            return fn(self, mutation, info, instance)

        _decorated._object_permission = mutation
        return _decorated

    return decorate


class BasePermission(object):
    """Basic permission class to be extended by any permission implementation.

    In combination with the decorators `@permission_for` and `@object_permission_for` a custom
    permission class can define permission on basis of mutations and its subclasses.

    Per default it returns True but default can be overwritten to define a permission for
    `Mutation`

    A custom permission class could look like this:
    ```
    >>> from caluma.form.schema import SaveForm
    ...
    ... class CustomPermission(BasePermission):
    ...     @permission_for(Mutation)
    ...     def has_permission_default(self, mutation, info):
    ...         # change default permission to False when no more specifc
    ...         # permission is defined.
    ...         return False
    ...
    ...     @permission_for(SaveForm)
    ...     def has_permission_for_save_form(self, mutation, info):
    ...         return True
    ...
    ...     @object_permission_for(SaveForm)
    ...     def has_object_permission_for_save_form(self, mutation, info, instance):
    ...         return instance.slug != 'protected-form'
    """

    def __init__(self):
        perms = inspect.getmembers(self, lambda m: hasattr(m, "_permission"))
        self._permissions = {fn._permission: fn for _, fn in perms}

        perms = inspect.getmembers(self, lambda m: hasattr(m, "_object_permission"))
        self._object_permissions = {fn._object_permission: fn for _, fn in perms}

    def has_permission(self, mutation, info):
        for cls in mutation.mro():
            if cls in self._permissions:
                return self._permissions[cls](mutation, info)

        return True

    def has_object_permission(self, mutation, info, instance):
        for cls in mutation.mro():
            if cls in self._object_permissions:
                return self._object_permissions[cls](mutation, info, instance)

        return True


class AllowAny(BasePermission):
    @permission_for(Mutation)
    def has_permission_default(self, mutation, info):
        return True
