from django.conf import settings


class AnonymousUser(object):
    def __init__(self):
        self.username = None
        self.groups = []
        self.token = None
        self.userinfo = {}
        self.group = None

    @property
    def is_authenticated(self):
        return False

    def __str__(self):
        return "AnonymousUser"


class OIDCUser(object):
    def __init__(self, token, userinfo):
        self.token = token
        self.username = userinfo["sub"]
        self.userinfo = userinfo
        self.groups = userinfo.get(settings.OIDC_GROUPS_CLAIM) or []

    @property
    def group(self):
        return self.groups and self.groups[0]

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username
