import inspect
from functools import wraps

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

    In combination with the decorator `@queryset_for` a custom visibility class
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
        queryset_nodes = [str(fn._filter_queryset_for) for _, fn in queryset_fns]
        queryset_nodes_dups = list_duplicates(queryset_nodes)
        assert not queryset_nodes_dups, (
            f"`filter_queryset_for` defined multiple times for "
            f"{', '.join(queryset_nodes_dups)} in {str(self)}"
        )
        self._filter_querysets_for = {
            fn._filter_queryset_for: fn for _, fn in queryset_fns
        }

    def get_queryset(self, node, queryset, info):
        for cls in reversed(node.mro()):
            if cls in self._filter_querysets_for:
                queryset = self._filter_querysets_for[cls](node, queryset, info)

        return queryset


class Any(BaseVisibility):
    """No restrictions, all nodes are exposed."""

    pass
