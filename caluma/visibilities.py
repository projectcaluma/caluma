from graphene.utils.str_converters import to_snake_case


class BaseVisibility(object):
    """Basic visibility classes to be extended by any visibility implementation."""

    def get_base_queryset(self, node, queryset, info):
        """
        Get base queryset.

        Override to implement default visiblity filters for all nodes.
        """
        return queryset

    def get_queryset(self, node, queryset, info):
        """
        Get queryset of specific node.

        Checks for node specific implement by its snake name.

        e.g. for Node WorkItem it will call `get_queryset_for_work_item` if available.
        """
        queryset = self.get_base_queryset(node, queryset, info)

        method_name = f"get_queryset_for_{to_snake_case(node.__name__)}"
        get_queryset_for_node = getattr(self, method_name, None)
        if get_queryset_for_node is not None:
            queryset = get_queryset_for_node(node, queryset, info)

        return queryset


class Any(BaseVisibility):
    """No restrictions, all nodes are exposed."""

    pass
