import pytest
from django.core.exceptions import ImproperlyConfigured

from .. import models
from ..types import DjangoObjectType
from ..visibilities import BaseVisibility, filter_queryset_for
from .fake_model import get_fake_model


def test_custom_visibility_override_filter_queryset_for_custom_node(db):
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
    queryset = CustomVisibility().filter_queryset(CustomNode, queryset, None)
    assert queryset.count() == 0


def test_custom_visibility_override_filter_queryset_with_duplicates(db):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    FakeModel.objects.create()

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    class CustomVisibility(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(
            self, node, queryset, info
        ):  # pragma: no cover
            return queryset.none()

        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node_2(
            self, node, queryset, info
        ):  # pragma: no cover
            return queryset.none()

    with pytest.raises(ImproperlyConfigured):
        CustomVisibility()


def test_custom_node_filter_queryset_improperly_configured(db):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    FakeModel.objects.create()

    class CustomNode(DjangoObjectType):
        visibility_classes = None

        class Meta:
            model = FakeModel

    with pytest.raises(ImproperlyConfigured):
        CustomNode.get_queryset(None, None)
