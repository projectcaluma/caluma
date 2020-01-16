import pytest

from ...caluma_core.models import UUIDModel
from ...caluma_core.tests.fake_model import get_fake_model
from .. import permissions


@pytest.mark.parametrize(
    "info_fixture,is_authenticated", [("info", False), ("admin_info", True)]
)
def test_is_authenticated_permission(db, info_fixture, is_authenticated, request):
    info = request.getfixturevalue(info_fixture)
    assert permissions.IsAuthenticated().has_permission(None, info) == is_authenticated


@pytest.mark.parametrize(
    "admin_groups,is_created_by", [(["admin_group"], True), (["nogroup"], False)]
)
def test_created_by_group_permission(db, admin_info, is_created_by, history_mock):
    FakeModel = get_fake_model(model_base=UUIDModel)
    instance = FakeModel.objects.create(created_by_group="admin_group")
    assert (
        permissions.CreatedByGroup().has_object_permission(None, admin_info, instance)
        == is_created_by
    )
