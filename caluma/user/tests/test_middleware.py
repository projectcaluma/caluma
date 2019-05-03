import hashlib
import json

import pytest
from django.core.cache import cache

from ...schema import schema
from .. import middleware


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
def test_oidc_authentication_middleware(
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
        userinfo = {"client_id": "test_client"}
        requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=401)
        requests_mock.post(settings.OIDC_INTROSPECT_ENDPOINT, text=json.dumps(userinfo))

    request = rf.get("/graphql", HTTP_AUTHORIZATION=authentication_header)

    query = """
    {
      __schema {
        mutationType {
          name
          description
        }
      }
    }
    """

    result = schema.execute(
        query, context=request, middleware=[middleware.OIDCAuthenticationMiddleware()]
    )
    assert bool(result.errors) == error
    key = "userinfo" if is_id_token else "introspect"
    if not error:
        assert request.user.is_authenticated == authenticated
        if authenticated:
            assert (
                cache.get(
                    f"authentication.{key}.{hashlib.sha256(b'Token').hexdigest()}"
                )
                == userinfo
            )


@pytest.mark.parametrize("introspection", [False, True])
def test_oidc_authentication_middleware_400(introspection, rf, requests_mock, settings):
    requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=400)

    if introspection:
        requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, status_code=401)
        requests_mock.post(settings.OIDC_INTROSPECT_ENDPOINT, status_code=400)
    elif not introspection:
        settings.OIDC_INTROSPECT_ENDPOINT = None

    request = rf.get("/graphql", HTTP_AUTHORIZATION="Bearer Token")

    query = """
    {
      __schema {
        mutationType {
          name
          description
        }
      }
    }
    """

    result = schema.execute(
        query, context=request, middleware=[middleware.OIDCAuthenticationMiddleware()]
    )
    assert result.errors
    assert (
        result.errors[0].message
        == f'400 Client Error: None for url: mock://caluma.io/openid/{"introspect" if introspection else "userinfo"}'
    )


def test_oidc_authentication_middleware_improperly_configured(rf, settings):
    settings.OIDC_USERINFO_ENDPOINT = None
    request = rf.get("/graphql", HTTP_AUTHORIZATION="Bearer Token")

    query = """
    {
      __schema {
        mutationType {
          name
          description
        }
      }
    }
    """

    result = schema.execute(
        query, context=request, middleware=[middleware.OIDCAuthenticationMiddleware()]
    )
    assert bool(result.errors)
