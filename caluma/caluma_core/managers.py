from django.conf import settings
from django.db.models import QuerySet
from django.utils.module_loading import import_string


def register_custom_managers():
    for cls_name in settings.MANAGER_CLASSES:
        manager_cls = import_string(cls_name)
        model_cls = manager_cls.Meta.model
        manager_name = manager_cls.Meta.name

        model_cls.add_to_class(
            manager_name,
            manager_cls.as_manager()
            if issubclass(manager_cls, QuerySet)
            else manager_cls(),
        )
