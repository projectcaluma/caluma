import hashlib
import json

import pytest
from django.core.cache import cache

from ...schema import schema
from .. import middleware


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
    rf, authentication_header, authenticated, error, requests_mock, settings
):
    userinfo = {"sub": "1"}
    requests_mock.get(settings.OIDC_USERINFO_ENDPOINT, text=json.dumps(userinfo))
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
    if not error:
        assert request.user.is_authenticated == authenticated
        if authenticated:
            assert (
                cache.get(
                    f"authentication.userinfo.{hashlib.sha256(b'Token').hexdigest()}"
                )
                == userinfo
            )
