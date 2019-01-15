import inspect
from functools import wraps

from django.core.exceptions import ImproperlyConfigured

from .collections import list_duplicates


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
    ... from caluma.mutation import Mutation
    ...
    ... class CustomPermission(BasePermission):
    ...     @permission_for(Mutation)
    ...     def has_permission_default(self, mutation, info):
    ...         # change default permission to False when no more specific
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
        perm_fns = inspect.getmembers(self, lambda m: hasattr(m, "_permission"))
        perm_muts = [fn._permission.__name__ for _, fn in perm_fns]
        perm_muts_dups = list_duplicates(perm_muts)
        if perm_muts_dups:
            raise ImproperlyConfigured(
                f"`permission_for` defined multiple times for "
                f"{', '.join(perm_muts_dups)} in {str(self)}"
            )
        self._permissions = {fn._permission: fn for _, fn in perm_fns}

        obj_perm_fns = inspect.getmembers(
            self, lambda m: hasattr(m, "_object_permission")
        )
        obj_perm_muts = [fn._object_permission.__name__ for _, fn in obj_perm_fns]
        obj_perm_muts_dups = list_duplicates(obj_perm_muts)
        if obj_perm_muts_dups:
            raise ImproperlyConfigured(
                f"`object_permission_for` defined multiple times for "
                f"{', '.join(obj_perm_muts_dups)} in {str(self)}"
            )
        self._object_permissions = {fn._object_permission: fn for _, fn in obj_perm_fns}

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
    pass
