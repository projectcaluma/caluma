# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.conf.urls import url

from .user.views import AuthenticationGraphQLView

urlpatterns = [
    url(
        r"^graphql",
        AuthenticationGraphQLView.as_view(graphiql=settings.DEBUG),
        name="graphql",
    )
]
