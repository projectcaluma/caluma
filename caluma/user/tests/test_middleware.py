import json
import time

import pytest
from django.conf import settings
from jose import jwt

from .. import middleware
from ...schema import schema

EXPIRED_TOKEN = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IjNlNTJhNzdiZDFiNDgwZDE0ZTA3MGZjZDQwNTU0Zjc5In0.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvb3BlbmlkIiwic3ViIjoiMSIsImF1ZCI6IjcwNjQ1MyIsImV4cCI6MTUzOTE4MjU3MCwiaWF0IjoxNTM5MTgxOTcwLCJhdXRoX3RpbWUiOjE1MzkxNjQ1ODgsIm5vbmNlIjoiMWtqdmM2biIsImF0X2hhc2giOiJCV2ZaR0dnWGlBMW5jbk5jeF90bHN3In0.emdEmsN6S9QEBc7fStxHEc_0lYPpY-G2c953gutyy70EfnltLt_GGMDKUY1NDM4ZeKUQP-vp6cAW7dcNHSrgg8xPkp65nPuRUBUVo68lEENG-EyrDG6AnQj5w474meALPch-peZgpPjR0zvj4LFJCi4KuWOBtBaiuFe7n3thWog"

KEYS = {
    "keys": [
        {
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": "3e52a77bd1b480d14e070fcd40554f79",
            "n": "7P5mh6TCYUPFPAeig-3ZqaqGgXnQuNcRGNowCgAUg8XJ2mfL0F07M27hTOmJIv15j68s3tkk1MEOy4xq436ArgKfy7utrTzOf9kC9maVg1w1RwXiprVzRAR0yM3gfn3hAlQ2TBaI7_ICasJgXpM1BC6q-baLUy9DqobhoprqpvE",
            "e": "AQAB",
        }
    ]
}


def valid_token():
    token = {
        "iss": settings.OIDC_JWKS_ENDPOINT,
        "sub": "1",
        "aud": settings.OIDC_CLIENT,
        "exp": time.time() + 60 * 60 * 24,
    }

    return f'Bearer {jwt.encode(token, settings.OIDC_SECRET_KEY, algorithm="HS256")}'


@pytest.mark.parametrize(
    "token,algorithm,authenticated,error",
    [
        ("", "", False, False),
        ("Bearer", "RS256", False, True),
        ("Bearer Too many params", "RS256", False, True),
        ("Basic Auth", "", False, True),
        ("Bearer InvalidToken", "RS256", False, True),
        (EXPIRED_TOKEN, "RS256", False, True),
        (valid_token(), "HS256", True, False),
    ],
)
def test_oidc_authentication_middleware(
    rf, token, algorithm, error, authenticated, requests_mock, settings
):
    settings.OIDC_VERIFY_ALGORITHM = algorithm
    requests_mock.get(settings.OIDC_JWKS_ENDPOINT, text=json.dumps(KEYS))

    request = rf.get("/graphql", HTTP_AUTHORIZATION=token)

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
