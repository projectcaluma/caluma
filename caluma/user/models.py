from django.conf import settings


class AnonymousUser(object):
    def __init__(self):
        self.username = None
        self.groups = []
        self.group = None

    @property
    def is_authenticated(self):
        return False

    def __str__(self):
        return "AnonymousUser"


class OIDCUser(object):
    def __init__(self, jwt_token):
        self.username = jwt_token["sub"]
        self.groups = jwt_token.get(settings.OIDC_GROUPS_CLAIM) or []

    @property
    def group(self):
        return self.groups and self.groups[0]

    @property
    def is_authenticated(self):
        return True

    def __str__(self):
        return self.username
