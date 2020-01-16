import pytest

from ...caluma_core.models import UUIDModel
from ...caluma_core.tests.fake_model import get_fake_model
from ...caluma_core.types import DjangoObjectType
from ..visibilities import Authenticated, CreatedByGroup


@pytest.mark.parametrize("info_fixture,size", [("info", 0), ("admin_info", 1)])
def test_authenticated_visibility(db, info_fixture, size, request, history_mock):
    info = request.getfixturevalue(info_fixture)
    FakeModel = get_fake_model(model_base=UUIDModel)

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    FakeModel.objects.create()

    queryset = Authenticated().filter_queryset(CustomNode, FakeModel.objects, info)
    assert queryset.count() == size


@pytest.mark.parametrize("group,size", [("unknown", 0), ("group", 1)])
def test_created_by_group_visibility(
    db, admin_info, group, admin_user, size, history_mock
):
    admin_user.groups = [group]
    FakeModel = get_fake_model(model_base=UUIDModel)

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    FakeModel.objects.create(created_by_group="group")

    queryset = CreatedByGroup().filter_queryset(
        CustomNode, FakeModel.objects, admin_info
    )
    assert queryset.count() == size
