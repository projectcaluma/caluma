from functools import wraps


def register_dynamic_group(dynamic_group_name):
    """Decorate function to register a dynamic group."""

    def wrapper(fn, *arg, **kwarg):
        fn._dynamic_group_name = dynamic_group_name

        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            return fn(self, *args, **kwargs)

        return wrapped

    return wrapper


class BaseDynamicGroups:
    """Basic dynamic groups class to be extended by any dynamic groups class implementation.

    In combination with the decorator `@register_dynamic_group` a dynamic group
    class can extend the JEXL `groups` transform used in the `address_groups`
    and `control_groups` property of a task.

    A dynamic groups class could look like this:

    >>> from your.project.code import find_legal_dept
    ... from caluma.caluma_workflow.dynamic_groups import (
    ...     BaseDynamicGroups,
    ...     register_dynamic_group,
    ... )
    ...
    ...
    ... class CustomDynamicGroups(BaseDynamicGroups):
    ...     @register_dynamic_group("legal_dept")
    ...     def resolve_legal_dept(self, task, case, user, prev_work_item, context):
    ...         # custom business logic which returns either a string or a list of strings
    ...         return find_legal_dept(case)
    """

    def resolve(self, dynamic_group_name):
        for methodname in dir(self):
            method = getattr(self, methodname)
            if (
                hasattr(method, "_dynamic_group_name")
                and method._dynamic_group_name == dynamic_group_name
            ):
                return method
