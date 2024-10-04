import inspect

from django.core.exceptions import ImproperlyConfigured

from .collections import list_duplicates


def filter_queryset_for(node):
    """Decorate function to define filtering of queryset of specific node."""

    def decorate(fn):
        if not hasattr(fn, "_visibilities"):
            fn._visibilities = []

        fn._visibilities.append(node)
        return fn

    return decorate


class BaseVisibility(object):
    """Basic visibility classes to be extended by any visibility implementation.

    In combination with the decorator `@filter_queryset_for` a custom visibility class
    can define filtering on basis of nodes and its subclasses.

    A custom visibility class could look like this:
    ```
    >>> from caluma.types import Node
    ... from caluma.caluma_form.schema import Form
    ...
    ... class CustomVisibility(BaseVisibility):
    ...     @filter_queryset_for(Node)
    ...     def filter_queryset_for_all(self, node, queryset, info):
    ...         return queryset.filter(created_by_user=info.context.request.user.username)
    ...
    ...     @filter_queryset_for(Form)
    ...     def filter_queryset_for_form(self, node, queryset, info):
    ...         return queryset.exclude(slug='protected-form')
    ...
    ...     # Do not trigger visibility when looking up case from workitem
    ...     suppress_visibilities = [
    ...         "WorkItem.case",
    ...         "WorkItem.child_case",
    ...     ]
    """

    # Used by the @suppressable_visibility decorator to store
    # the *allowed* values for the `suppress_visibilities` property
    _suppressable_visibilities = set()

    def __init__(self):
        queryset_fns = inspect.getmembers(self, lambda m: hasattr(m, "_visibilities"))

        queryset_nodes = [
            node.__name__ for _, fn in queryset_fns for node in fn._visibilities
        ]
        queryset_nodes_dups = list_duplicates(queryset_nodes)
        if queryset_nodes_dups:
            raise ImproperlyConfigured(
                f"`filter_queryset_for` defined multiple times for "
                f"{', '.join(queryset_nodes_dups)} in {str(self)}"
            )

        self._filter_querysets_for = {
            node: fn for _, fn in queryset_fns for node in fn._visibilities
        }

        self._validate_suppress_visibility()

    def _validate_suppress_visibility(self):
        requested_suppressors = set(self.suppress_visibilities)
        available_suppressors = type(self)._suppressable_visibilities

        invalid = requested_suppressors - available_suppressors
        if invalid:  # pragma: no cover
            invalid_str_list = ", ".join(f"`{x}`" for x in (sorted(invalid)))
            raise ImproperlyConfigured(
                f"`{type(self).__name__}` contains invalid `suppress_visibilities`: "
                f"{invalid_str_list}"
            )

    def filter_queryset(self, node, queryset, info):
        for cls in node.mro():
            if cls in self._filter_querysets_for:
                return self._filter_querysets_for[cls](node, queryset, info)

        return queryset

    # Default: suppress no visibilities
    suppress_visibilities = []


class Any(BaseVisibility):
    """No restrictions, all nodes are exposed."""

    pass


class Union(BaseVisibility):
    """Union result of a list of configured visibility classes."""

    visibility_classes = []

    def filter_queryset(self, node, queryset, info):
        result_queryset = None
        for visibility_class in self.visibility_classes:
            class_result = (
                visibility_class().filter_queryset(node, queryset, info).all()
            )
            if result_queryset is None:
                result_queryset = class_result
            else:
                result_queryset = result_queryset.union(class_result)

        if result_queryset is not None:
            queryset = queryset.filter(pk__in=result_queryset.values("pk"))

        return queryset
