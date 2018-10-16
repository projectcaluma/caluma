import pytest

from ..permissions import IsAuthenticated


@pytest.mark.parametrize(
    "info_fixture,is_authenticated", [("info", False), ("admin_info", True)]
)
def test_is_authenticated_permission(db, info_fixture, is_authenticated, request):
    info = request.getfixturevalue(info_fixture)
    assert IsAuthenticated().has_permission(None, info) == is_authenticated
