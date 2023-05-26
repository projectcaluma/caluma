import hashlib
import json

import pytest
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status

from .. import views


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
    requests_mock,
    settings,
):
    userinfo = {"sub": "1"}
    requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, text=json.dumps(userinfo))

    request = rf.get("/graphql", HTTP_AUTHORIZATION=authentication_header)
    response = views.AuthenticationGraphQLView.as_view()(request)
    assert bool(response.status_code == status.HTTP_401_UNAUTHORIZED) == error
    if not error:
        assert request.user.is_authenticated == authenticated
        if authenticated:
            assert (
                cache.get(
                    f"authentication.userinfo.{hashlib.sha256(b'Token').hexdigest()}"
                )
                == userinfo
            )


def test_authentication_invalid_provider(rf, requests_mock, settings):
    requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=400)

    request = rf.get("/graphql", HTTP_AUTHORIZATION="Bearer Token")
    response = views.AuthenticationGraphQLView.as_view()(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    result = json.loads(response.content)
    assert (
        result["errors"][0]["message"]
        == "400 Client Error: None for url: mock://caluma.io/openid/userinfo"
    )


def test_authentication_view_improperly_configured(rf, settings):
    settings.OIDC_USERINFO_ENDPOINT = None
    request = rf.get("/graphql", HTTP_AUTHORIZATION="Bearer Token")
    with pytest.raises(ImproperlyConfigured):
        views.AuthenticationGraphQLView.as_view()(request)
