import inspect
from functools import wraps

from django.core.exceptions import ImproperlyConfigured

from .collections import list_duplicates


def filter_queryset_for(node):
    """Decorate function to define filtering of queryset of specific node."""

    def decorate(fn):
        @wraps(fn)
        def _decorated(self, node, queryset, info):
            return fn(self, node, queryset, info)

        _decorated._filter_queryset_for = node
        return _decorated

    return decorate


class BaseVisibility(object):
    """Basic visibility classes to be extended by any visibility implementation.

    In combination with the decorator `@filter_queryset_for` a custom visibility class
    can define filtering on basis of nodes and its subclasses.

    A custom visibility class could look like this:
    ```
    >>> from caluma.types import Node
    ... from caluma.form.schema import Form
    ...
    ... class CustomVisibility(BaseVisibility):
    ...     @filter_queryset_for(Node)
    ...     def filter_queryset_for_all(self, node, queryset, info):
    ...         return queryset.filter(created_by_user=info.context.request.user.username)
    ...
    ...     @filter_queryset_for(Form)
    ...     def filter_queryset_for_form(self, node, queryset, info):
    ...         return queryset.exclude(slug='protected-form')
    """

    def __init__(self):
        queryset_fns = inspect.getmembers(
            self, lambda m: hasattr(m, "_filter_queryset_for")
        )
        queryset_nodes = [fn._filter_queryset_for.__name__ for _, fn in queryset_fns]
        queryset_nodes_dups = list_duplicates(queryset_nodes)
        if queryset_nodes_dups:
            raise ImproperlyConfigured(
                f"`filter_queryset_for` defined multiple times for "
                f"{', '.join(queryset_nodes_dups)} in {str(self)}"
            )
        self._filter_querysets_for = {
            fn._filter_queryset_for: fn for _, fn in queryset_fns
        }

    def filter_queryset(self, node, queryset, info):
        for cls in node.mro():
            if cls in self._filter_querysets_for:
                queryset = self._filter_querysets_for[cls](node, queryset, info)

        return queryset


class Any(BaseVisibility):
    """No restrictions, all nodes are exposed."""

    pass


class Union(BaseVisibility):
    """Union result of a list of configured visibility classes."""

    visibility_classes = []

    def filter_queryset(self, node, queryset, info):
        result_queryset = None
        for visibility_class in self.visibility_classes:
            class_result = visibility_class().filter_queryset(node, queryset, info)
            if result_queryset is None:
                result_queryset = class_result
            else:
                result_queryset = result_queryset.union(class_result)

        return result_queryset or queryset
