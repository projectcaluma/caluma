from ..caluma_core.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """Only allow authenticated users to execute mutations."""

    def has_permission(self, mutation, info):
        return info.context.user.is_authenticated


class CreatedByGroup(BasePermission):
    """Only allow mutating data that belongs to same group as current user."""

    def has_object_permission(self, mutation, info, instance):
        return instance.created_by_group in info.context.user.groups
