# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse


def test_graphql_url(client):
    assert reverse("graphql")
