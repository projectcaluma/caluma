from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string


class DefaultConfig(AppConfig):
    name = "caluma.core"

    def ready(self):
        from .mutation import Mutation
        from .types import Node

        # to avoid recursive import error, load extension classes
        # only once the app is ready
        Mutation.permission_classes = [
            import_string(cls) for cls in settings.PERMISSION_CLASSES
        ]
        Node.visibility_classes = [
            import_string(cls) for cls in settings.VISIBILITY_CLASSES
        ]
