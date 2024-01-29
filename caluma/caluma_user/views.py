import functools
import hashlib

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.encoding import force_bytes, smart_str
from django.utils.module_loading import import_string
from graphene.validation import DisableIntrospection
from graphene_django.views import GraphQLView, HttpError
from rest_framework.authentication import get_authorization_header

from caluma.caluma_user import models


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


class AuthenticationGraphQLView(GraphQLView):
    if settings.DISABLE_INTROSPECTION:  # pragma: no cover
        validation_rules = (DisableIntrospection,)

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
        response = requests.get(
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
