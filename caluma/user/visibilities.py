from ..visibilities import BaseVisibility


class Authenticated(BaseVisibility):
    """Only allow authenticated users to read nodes."""

    def get_base_queryset(self, node, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()


class CreatedByGroup(BaseVisibility):
    """User may only read nodes of created by group it belongs to."""

    def get_base_queryset(self, node, queryset, info):
        groups = info.context.user.groups
        return queryset.filter(created_by_group__in=groups)
