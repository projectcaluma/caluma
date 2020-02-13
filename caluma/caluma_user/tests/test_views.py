import hashlib
import json

import pytest
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status

from .. import views


@pytest.mark.parametrize("is_id_token", [True, False])
@pytest.mark.parametrize(
    "authentication_header,authenticated,error",
    [
        ("", False, False),
        ("Bearer", False, True),
        ("Bearer Too many params", False, True),
        ("Basic Auth", False, True),
        ("Bearer Token", True, False),
    ],
)
def test_authentication_view(
    rf,
    authentication_header,
    authenticated,
    error,
    is_id_token,
    requests_mock,
    settings,
):
    userinfo = {"sub": "1"}
    requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, text=json.dumps(userinfo))

    if not is_id_token:
        userinfo = {"client_id": "test_client", "sub": "service-account-foo-bar"}
        requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=401)
        requests_mock.post(settings.OIDC_INTROSPECT_ENDPOINT, text=json.dumps(userinfo))

    request = rf.get("/graphql", HTTP_AUTHORIZATION=authentication_header)
    response = views.AuthenticationGraphQLView.as_view()(request)
    assert bool(response.status_code == status.HTTP_401_UNAUTHORIZED) == error
    if not error:
        key = "userinfo" if is_id_token else "introspect"

        assert request.user.is_authenticated == authenticated
        if authenticated:
            assert (
                cache.get(
                    f"authentication.{key}.{hashlib.sha256(b'Token').hexdigest()}"
                )
                == userinfo
            )


@pytest.mark.parametrize("introspection", [False, True])
def test_authentication_invalid_provider(introspection, rf, requests_mock, settings):
    requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=400)

    if introspection:
        requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=401)
        requests_mock.post(settings.OIDC_INTROSPECT_ENDPOINT, status_code=400)
    elif not introspection:
        settings.OIDC_INTROSPECT_ENDPOINT = None

    request = rf.get("/graphql", HTTP_AUTHORIZATION="Bearer Token")
    response = views.AuthenticationGraphQLView.as_view()(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert (
        result["errors"][0]["message"]
        == f'400 Client Error: None for url: mock://caluma.io/openid/{"introspect" if introspection else "userinfo"}'
    )


def test_authentication_view_improperly_configured(rf, settings):
    settings.OIDC_USERINFO_ENDPOINT = None
    request = rf.get("/graphql", HTTP_AUTHORIZATION="Bearer Token")
    with pytest.raises(ImproperlyConfigured):
        views.AuthenticationGraphQLView.as_view()(request)


def test_no_client_id(rf, requests_mock, settings):
    cache.clear()
    authentication_header = "Bearer Token"
    userinfo = {"sub": "1"}
    requests_mock.get(
        settings.OIDC_USERINFO_ENDPOINT, text=json.dumps(userinfo), status_code=401
    )
    requests_mock.post(settings.OIDC_INTROSPECT_ENDPOINT, text=json.dumps(userinfo))

    request = rf.get("/graphql", HTTP_AUTHORIZATION=authentication_header)
    response = views.AuthenticationGraphQLView.as_view()(request)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
