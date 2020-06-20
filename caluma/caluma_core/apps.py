from importlib import import_module

from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string


class DefaultConfig(AppConfig):
    name = "caluma.caluma_core"

    def ready(self):
        from .mutation import Mutation
        from .types import Node
        from .serializers import ModelSerializer

        # to avoid recursive import error, load extension classes
        # only once the app is ready
        Mutation.permission_classes = [
            import_string(cls) for cls in settings.PERMISSION_CLASSES
        ]
        ModelSerializer.validation_classes = [
            import_string(cls) for cls in settings.VALIDATION_CLASSES
        ]
        Node.visibility_classes = [
            import_string(cls) for cls in settings.VISIBILITY_CLASSES
        ]
        for module in settings.EVENT_RECEIVER_MODULES:
            import_module(module)

        import_module("caluma.caluma_form.signals")
