from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string


class DefaultConfig(AppConfig):
    name = "caluma.caluma_workflow"

    def ready(self):
        from .jexl import GroupJexl, FlowJexl

        # to avoid recursive import error, load extension classes
        # only once the app is ready
        GroupJexl.dynamic_groups_classes = [
            import_string(cls) for cls in settings.DYNAMIC_GROUPS_CLASSES
        ]
        FlowJexl.dynamic_tasks_classes = [
            import_string(cls) for cls in settings.DYNAMIC_TASKS_CLASSES
        ]
