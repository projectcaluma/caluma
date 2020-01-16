from ..caluma_core.types import Node
from ..caluma_core.visibilities import BaseVisibility, filter_queryset_for


class Authenticated(BaseVisibility):
    """Only allow authenticated users to read nodes."""

    @filter_queryset_for(Node)
    def filter_queryset_for_all(self, node, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()


class CreatedByGroup(BaseVisibility):
    """User may only read nodes of created by group it belongs to."""

    @filter_queryset_for(Node)
    def filter_queryset_for_all(self, node, queryset, info):
        groups = info.context.user.groups
        return queryset.filter(created_by_group__in=groups)
