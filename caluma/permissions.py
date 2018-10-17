from graphene.utils.str_converters import to_snake_case


class BasePermission(object):
    """Basic permission class to be extended by any permission implementation."""

    def has_permission(self, mutation, info):
        """
        Check permission of specific mutation or otherwise return True.

        Checks for mutation specific implementations by its snake name.

        e.g. for mutation SaveDocument it will call `has_permission_for_save_document` if available.
        """
        method_name = f"has_permission_for_{to_snake_case(mutation.__name__)}"
        has_permission_for_mutation = getattr(self, method_name, None)
        if has_permission_for_mutation is not None:
            return has_permission_for_mutation(mutation, info)

        return True

    def has_object_permission(self, mutation, info, instance):
        """
        Check object permission of specific mutation or otherwise return True.

        Checks for mutation specific implementations by its snake name.

        e.g. for mutation SaveDocument it will call `has_object_permission_for_save_document` if available.
        """
        method_name = f"has_object_permission_for_{to_snake_case(mutation.__name__)}"
        has_object_permission_for_mutation = getattr(self, method_name, None)
        if has_object_permission_for_mutation is not None:
            return has_object_permission_for_mutation(mutation, info, instance)

        return True


class AllowAny(BasePermission):
    pass
