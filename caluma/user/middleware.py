import requests
from django.conf import settings
from django.utils.encoding import smart_text
from jose import ExpiredSignatureError, JWTError, jwt
from rest_framework.authentication import get_authorization_header

from . import models


class OIDCAuthenticationMiddleware(object):
    """GraphQL middleware to authenticate against open id connect provider.

    This middle enforces authentication for all graphs.
    """

    def __init__(self):
        self._keys = None

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        header_prefix = "Bearer"

        if not auth:
            return None

        if smart_text(auth[0].lower()) != header_prefix.lower():
            raise JWTError("No Bearer Authorization header")

        if len(auth) == 1:
            msg = "Invalid Authorization header. No credentials provided"
            raise JWTError(msg)
        elif len(auth) > 2:
            msg = (
                "Invalid Authorization header. Credentials string should "
                "not contain spaces."
            )
            raise JWTError(msg)

        return auth[1]

    def get_json(self, url):
        response = requests.get(url, verify=settings.OIDC_VERIFY_SSL)
        response.raise_for_status()
        return response.json()

    def decode_token(self, token, key):
        return jwt.decode(
            token=token,
            key=key,
            options=settings.OIDC_VALIDATE_CLAIMS_OPTIONS,
            algorithms=[settings.OIDC_VERIFY_ALGORITHM],
            audience=settings.OIDC_CLIENT,
        )

    def keys(self):
        if settings.OIDC_VERIFY_ALGORITHM.startswith("RS"):
            if self._keys is None:
                self._keys = self.get_json(settings.OIDC_JWKS_ENDPOINT)
        else:
            self._keys = settings.OIDC_SECRET_KEY

        return self._keys

    def resolve(self, next, root, info, **args):
        request = info.context
        jwt_value = self.get_jwt_value(request)

        if jwt_value is None:
            request.user = models.AnonymousUser()
            return next(root, info, **args)

        # TODO: status code of jwt error should be 401
        # https://github.com/graphql-python/graphene-django/issues/252
        try:
            decoded_token = self.decode_token(jwt_value, self.keys())
        except ExpiredSignatureError:
            raise
        except JWTError:
            # try again with refreshed keys
            self._keys = None
            decoded_token = self.decode_token(jwt_value, self.keys())

        request.user = models.OIDCUser(jwt_value, decoded_token)
        return next(root, info, **args)
