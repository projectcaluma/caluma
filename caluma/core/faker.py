# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from faker import Faker
from faker.providers.date_time import Provider


class MultilangProvider(Provider):
    """
    Create dictionary compatible with `LocalizedField`.

    A value with given `faker_provider` is created for given languages.
    """

    def multilang(self, faker_provider, languages=("en", "de"), **kwargs):
        value = {}
        for language in languages:
            value[language] = getattr(Faker(language), faker_provider)(*kwargs)

        return value
