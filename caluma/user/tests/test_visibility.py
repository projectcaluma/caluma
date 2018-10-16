import pytest

from ...models import UUIDModel
from ...tests.fake_model import get_fake_model
from ...types import DjangoObjectType
from ..visibilities import Authenticated


@pytest.mark.parametrize("info_fixture,size", [("info", 0), ("admin_info", 1)])
def test_authenticated_visibility(db, info_fixture, size, request):
    info = request.getfixturevalue(info_fixture)
    FakeModel = get_fake_model(model_base=UUIDModel)

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    FakeModel.objects.create()

    queryset = Authenticated().get_queryset(CustomNode, FakeModel.objects, info)
    assert queryset.count() == size
