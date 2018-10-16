from ..permissions import BasePermission


class IsAuthenticated(BasePermission):
    """Only allow authenticated users to execute mutations."""

    def has_permission(self, mutation, info):
        return info.context.user.is_authenticated
