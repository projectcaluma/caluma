import base64
import functools
import hashlib

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse
from django.utils.encoding import force_bytes, smart_str
from django.utils.module_loading import import_string
from graphene_django.views import GraphQLView, HttpError
from rest_framework.authentication import get_authorization_header

from caluma.caluma_user import models


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


class AuthenticationGraphQLView(GraphQLView):
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

    def get_introspection(self, token):
        basic = base64.b64encode(
            f"{settings.OIDC_INTROSPECT_CLIENT_ID}:{settings.OIDC_INTROSPECT_CLIENT_SECRET}".encode(
                "utf-8"
            )
        ).decode()
        headers = {
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            settings.OIDC_INTROSPECT_ENDPOINT,
            verify=settings.OIDC_VERIFY_SSL,
            headers=headers,
            data={"token": token},
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
        # token might be too long for key so we use hash sum instead.
        hashsum_token = hashlib.sha256(force_bytes(token)).hexdigest()

        try:
            userinfo = cache.get_or_set(
                f"authentication.userinfo.{hashsum_token}",
                userinfo_method,
                timeout=settings.OIDC_BEARER_TOKEN_REVALIDATION_TIME,
            )
            return self._oidc_user(token=token, userinfo=userinfo)
        except requests.HTTPError as e:
            try:
                if (
                    e.response.status_code in [401, 403]
                    and settings.OIDC_INTROSPECT_ENDPOINT
                ):
                    introspect_method = functools.partial(
                        self.get_introspection, token=token
                    )
                    introspection = cache.get_or_set(
                        f"authentication.introspect.{hashsum_token}",
                        introspect_method,
                        timeout=settings.OIDC_BEARER_TOKEN_REVALIDATION_TIME,
                    )
                    if "client_id" not in introspection:
                        response = HttpResponse(status=401)
                        raise HttpError(response)
                    return self._oidc_user(token=token, introspection=introspection)
                else:
                    raise e
            except requests.HTTPError as internal_exception:
                # convert request error to django http error
                response = HttpResponse()
                response.status_code = internal_exception.response.status_code
                raise HttpError(response, message=str(internal_exception))

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
