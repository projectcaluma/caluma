from .. import models
from ..types import DjangoObjectType
from ..visibilities import BaseVisibility, filter_queryset_for
from .fake_model import get_fake_model


def test_custom_visibility_override_get_queryset_for_custom_node(db):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    FakeModel.objects.create()

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    class CustomVisibility(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.none()

    queryset = FakeModel.objects
    assert queryset.count() == 1
    queryset = CustomVisibility().get_queryset(CustomNode, queryset, None)
    assert queryset.count() == 0
