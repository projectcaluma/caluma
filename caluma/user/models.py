# SPDX-FileCopyrightText: 2019 Adfinis SyGroup AG
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


class BaseUser:  # pragma: no cover
    def __init__(self):
        self.username = None
        self.groups = []
        self.token = None
        self.userinfo = {}
        self.is_authenticated = False

    @property
    def group(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class AnonymousUser(BaseUser):
    @property
    def group(self):
        return None

    def __str__(self):
        return "AnonymousUser"


class OIDCUser(BaseUser):
    def __init__(self, token, userinfo):
        self.token = token
        self.username = userinfo["sub"]
        self.userinfo = userinfo
        self.groups = userinfo.get(settings.OIDC_GROUPS_CLAIM) or []
        self.is_authenticated = True

    @property
    def group(self):
        return self.groups[0] if self.groups else None

    def __str__(self):
        return self.username


class OIDCClient(BaseUser):
    def __init__(self, token, introspection):
        self.token = token
        self.username = f"system-{introspection['client_id']}"
        self.introspection = introspection
        self.is_authenticated = True

    @property
    def group(self):  # pragma: no cover
        return None

    def __str__(self):
        return self.username
