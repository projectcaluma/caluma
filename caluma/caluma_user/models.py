from django.conf import settings


class BaseUser:  # pragma: no cover
    def __init__(self, username=None, groups=None, group=None, token=None, claims=None):
        self.username = username
        self.groups = [] if groups is None else groups
        self.group = group
        self.token = token
        self.claims = {} if claims is None else claims
        self.is_authenticated = False

    def __str__(self):
        raise NotImplementedError


class AnonymousUser(BaseUser):
    def __str__(self):
        return "AnonymousUser"


class OIDCUser(BaseUser):
    def __init__(self, token: str, claims: dict):
        super().__init__(token=token, claims=claims)

        self.username = self.claims[settings.OIDC_USERNAME_CLAIM]
        self.groups = self.claims.get(settings.OIDC_GROUPS_CLAIM, [])
        self.group = self.groups[0] if self.groups else None
        self.token = token
        self.is_authenticated = True

    def __str__(self):
        return self.username
