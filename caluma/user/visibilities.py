from ..visibilities import BaseVisibility


class Authenticated(BaseVisibility):
    """Only allow authenticated users to read nodes."""

    def get_base_queryset(self, node, queryset, info):
        if info.context.user.is_authenticated:
            return queryset
        return queryset.none()
