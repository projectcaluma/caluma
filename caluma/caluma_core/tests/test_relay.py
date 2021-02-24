from base64 import b64encode

import pytest

from ..relay import extract_global_id


@pytest.mark.parametrize(
    "id,expected",
    [
        ("slug", "slug"),
        ("V29ya2Zsb3c6bGlzdGVuZWludHJhZw==", "listeneintrag"),
        ("b106", "b106"),
        (b64encode(b"NonExistantModel:foobar"),) * 2,
    ],
)
def test_extract_global_id(id, expected):
    assert extract_global_id(id) == expected
