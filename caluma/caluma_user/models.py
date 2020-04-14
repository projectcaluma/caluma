from warnings import warn

from django.conf import settings


class BaseUser:  # pragma: no cover
    def __init__(self):
        self.username = None
        self.groups = []
        self.group = None
        self.token = None
        self.claims = {}
        self.is_authenticated = False

    def __getattribute__(self, name):
        if name in ["userinfo", "introspection"]:
            warn(
                f'"{name}" is deprecated. Use the new "claims" attribute',
                DeprecationWarning,
            )
            return self.claims
        return super().__getattribute__(name)

    def __str__(self):
        raise NotImplementedError


class AnonymousUser(BaseUser):
    def __str__(self):
        return "AnonymousUser"


class OIDCUser(BaseUser):
    def __init__(self, token: str, userinfo: dict = None, introspection: dict = None):
        super().__init__()

        self.claims, self.claims_source = self._get_claims(userinfo, introspection)
        self.username = self.claims[settings.OIDC_USERNAME_CLAIM]
        self.groups = self.claims.get(settings.OIDC_GROUPS_CLAIM)
        self.group = self.groups[0] if self.groups else None
        self.token = token
        self.is_authenticated = True

    def _get_claims(self, userinfo, introspection):
        result = (userinfo, "userinfo")
        if all([userinfo, introspection]):  # pragma: no cover
            raise AttributeError("You can't set userinfo AND introspection.")
        elif not any([userinfo, introspection]):  # pragma: no cover
            raise AttributeError("You must provide either userinfo or introspection.")
        elif introspection is not None:
            result = (introspection, "introspection")
        return result

    def __str__(self):
        return self.username
