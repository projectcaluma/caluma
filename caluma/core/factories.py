# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from factory import Faker, django


class DjangoModelFactory(django.DjangoModelFactory):
    created_by_user = Faker("uuid4")
    created_by_group = Faker("uuid4")
