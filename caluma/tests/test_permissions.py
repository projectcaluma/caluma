from .. import models
from ..permissions import BasePermission
from ..types import DjangoObjectType
from .fake_model import get_fake_model


def test_custom_permission_override_has_permission_for_custom_node(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    instance = FakeModel.objects.create()

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    class CustomPermission(BasePermission):
        def has_permission_for_custom_node(self, mutation, info):
            return False

        def has_object_permission_for_custom_node(self, mutation, info, instance):
            return False

    assert not CustomPermission().has_permission(CustomNode, info)
    assert not CustomPermission().has_object_permission(CustomNode, info, instance)
