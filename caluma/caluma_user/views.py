import functools
import hashlib

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.encoding import force_bytes, smart_str
from django.utils.module_loading import import_string
from graphene.validation import DisableIntrospection, depth_limit_validator
from graphene_django.views import GraphQLView, HttpError
from rest_framework.authentication import get_authorization_header

from caluma.caluma_user import models


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


class SuppressIntrospection(DisableIntrospection):
    """Validate request to reject any introspection, except the bare minimum."""

    # The base class, graphene.validation.DisableIntrospection, is too strict:
    # It rejects everything starting with double underscores (as per GQL spec)
    # but we need `__typename` for our frontends to work correctly.

    ALLOWED_INTROSPECTION_KEYS = ["__typename"]

    def enter_field(self, node, *_args):
        field_name = node.name.value
        if field_name not in self.ALLOWED_INTROSPECTION_KEYS:
            super().enter_field(node, *_args)


custom_validation_rules = []
if settings.DISABLE_INTROSPECTION:  # pragma: no cover
    custom_validation_rules.append(SuppressIntrospection)

if settings.QUERY_DEPTH_LIMIT:  # pragma: no cover
    custom_validation_rules.append(
        depth_limit_validator(max_depth=settings.QUERY_DEPTH_LIMIT)
    )


class AuthenticationGraphQLView(GraphQLView):
    @classmethod
    def _requests_session(cls):
        """
        Return a requests session that's kept alive over time.

        We use a "global" requests session for auth, as the initialisation of
        SSL context and re-opening of a TCP connection to the OIDC IDP can cause
        some additional load (and work time) that we want to avoid if possible.
        """
        if not hasattr(cls, "_http_client"):
            setattr(cls, "_http_client", requests.Session())
        return cls._http_client

    if custom_validation_rules:  # pragma: no cover
        validation_rules = tuple(custom_validation_rules)

    def get_bearer_token(self, request):
        auth = get_authorization_header(request).split()
        header_prefix = "Bearer"

        if not auth:
            return None

        if smart_str(auth[0].lower()) != header_prefix.lower():
            raise HttpError(HttpResponseUnauthorized("No Bearer Authorization header"))

        if len(auth) == 1:
            msg = "Invalid Authorization header. No credentials provided"
            raise HttpError(HttpResponseUnauthorized(msg))
        elif len(auth) > 2:
            msg = (
                "Invalid Authorization header. Credentials string should "
                "not contain spaces."
            )
            raise HttpError(HttpResponseUnauthorized(msg))

        return auth[1]

    def get_userinfo(self, token):
        response = self._requests_session().get(
            settings.OIDC_USERINFO_ENDPOINT,
            verify=settings.OIDC_VERIFY_SSL,
            headers={"Authorization": f"Bearer {smart_str(token)}"},
        )
        response.raise_for_status()
        return response.json()

    def _oidc_user(self, *args, **kwargs):
        factory = import_string(settings.CALUMA_OIDC_USER_FACTORY)
        return factory(*args, **kwargs)

    def get_user(self, request):
        token = self.get_bearer_token(request)

        if token is None:
            return models.AnonymousUser()

        if not settings.OIDC_USERINFO_ENDPOINT:
            raise ImproperlyConfigured(
                'Token was provided, but "OIDC_USERINFO_ENDPOINT" is not set.'
            )

        userinfo_method = functools.partial(self.get_userinfo, token=token)
        # token might be too long for key, so we use hash sum instead.
        hashsum_token = hashlib.sha256(force_bytes(token)).hexdigest()

        try:
            claims = cache.get_or_set(
                f"authentication.userinfo.{hashsum_token}",
                userinfo_method,
                timeout=settings.OIDC_BEARER_TOKEN_REVALIDATION_TIME,
            )
        except requests.HTTPError as e:
            # convert request error to django http error
            response = HttpResponse()
            response.status_code = e.response.status_code
            raise HttpError(response, message=str(e))

        return self._oidc_user(token=token, claims=claims)

    def dispatch(self, request, *args, **kwargs):
        try:
            request.user = self.get_user(request)
            return super().dispatch(request, *args, **kwargs)
        except HttpError as e:
            response = e.response
            response["Content-Type"] = "application/json"
            response.content = self.json_encode(
                request, {"errors": [self.format_error(e)]}
            )
            return response
