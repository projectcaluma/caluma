# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.utils import translation


def translate_value(value):
    """Translate a string.

    :param value: dict or string
    :return: translated value or original string
    """
    lang = translation.get_language()
    if lang in value:
        return value[lang]
    if settings.LANGUAGE_CODE in value:
        return value[settings.LANGUAGE_CODE]
    return value
