# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string


class DefaultConfig(AppConfig):
    name = "caluma.core"

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
