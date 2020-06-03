import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db.models import CharField

from .. import models
from ..types import DjangoObjectType, Node
from ..visibilities import BaseVisibility, Union, filter_queryset_for
from .fake_model import get_fake_model


def test_custom_visibility_override_filter_queryset_for_custom_node(db, history_mock):
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


def test_custom_visibility_override_filter_queryset_with_duplicates(db, history_mock):
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


def test_custom_node_filter_queryset_improperly_configured(db, history_mock):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    FakeModel.objects.create()

    class CustomNode(DjangoObjectType):
        visibility_classes = None

        class Meta:
            model = FakeModel

    with pytest.raises(ImproperlyConfigured):
        CustomNode.get_queryset(None, None)


def test_custom_visibility_override_specificity(db, history_mock):
    """The first matching filter 'wins'."""
    FakeModel = get_fake_model(
        dict(name=CharField(max_length=255)), model_base=models.UUIDModel
    )
    FakeModel.objects.create(name="Name1")
    FakeModel.objects.create(name="Name2")

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    class CustomVisibility(BaseVisibility):
        @filter_queryset_for(Node)
        def filter_queryset_for_all(self, node, queryset, info):
            return queryset.none()

        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.filter(name="Name1")

    assert FakeModel.objects.count() == 2
    queryset = CustomVisibility().filter_queryset(Node, FakeModel.objects, None)
    assert queryset.count() == 0
    queryset = CustomVisibility().filter_queryset(CustomNode, FakeModel.objects, None)
    assert queryset.count() == 1


def test_union_visibility(db, history_mock):
    FakeModel = get_fake_model(
        dict(name=CharField(max_length=255)), model_base=models.UUIDModel
    )
    FakeModel.objects.create(name="Name1")
    FakeModel.objects.create(name="Name2")
    FakeModel.objects.create(name="Name3")
    FakeModel.objects.create(name="Name4")

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    class Name1Visibility(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.filter(name="Name1")

    class Name2Visibility(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.filter(name="Name2")

    class Name3Visibility(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.filter(name__in=["Name2", "Name3"])

    class ConfiguredUnion(Union):
        visibility_classes = [Name1Visibility, Name2Visibility, Name3Visibility]

    queryset = FakeModel.objects
    result = Name1Visibility().filter_queryset(CustomNode, queryset, None)
    assert result.count() == 1
    result = Name2Visibility().filter_queryset(CustomNode, queryset, None)
    assert result.count() == 1
    result = Name3Visibility().filter_queryset(CustomNode, queryset, None)
    assert result.count() == 2
    queryset = ConfiguredUnion().filter_queryset(CustomNode, queryset, None)
    assert queryset.count() == 3
    assert queryset.get(name="Name2")


def test_union_visibility_none(db, history_mock):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    FakeModel.objects.create()

    class CustomNode(DjangoObjectType):
        class Meta:
            model = FakeModel

    class CustomVisibility(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.none()

    class CustomVisibility2(BaseVisibility):
        @filter_queryset_for(CustomNode)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.none()

    class ConfiguredUnion(Union):
        visibility_classes = [CustomVisibility2, CustomVisibility]

    queryset = FakeModel.objects
    result = CustomVisibility().filter_queryset(CustomNode, queryset, None)
    assert result.count() == 0
    result = CustomVisibility2().filter_queryset(CustomNode, queryset, None)
    assert result.count() == 0
    queryset = ConfiguredUnion().filter_queryset(CustomNode, queryset, None)
    assert queryset.count() == 0


def test_custom_visibility_chained_decorators(db, history_mock):
    """The first matching filter 'wins'."""
    FakeModel1 = get_fake_model(
        dict(name=CharField(max_length=255)), model_base=models.UUIDModel
    )
    FakeModel1.objects.create(name="Name1")
    FakeModel1.objects.create(name="Name2")

    FakeModel2 = get_fake_model(
        dict(name=CharField(max_length=255)), model_base=models.UUIDModel
    )
    FakeModel2.objects.create(name="Name1")
    FakeModel2.objects.create(name="Name2")

    class CustomNode1(DjangoObjectType):
        class Meta:
            model = FakeModel1

    class CustomNode2(DjangoObjectType):
        class Meta:
            model = FakeModel2

    class CustomVisibility(BaseVisibility):
        @filter_queryset_for(Node)
        def filter_queryset_for_all(self, node, queryset, info):
            return queryset.none()

        @filter_queryset_for(CustomNode1)
        @filter_queryset_for(CustomNode2)
        def filter_queryset_for_custom_node(self, node, queryset, info):
            return queryset.filter(name="Name1")

    assert FakeModel1.objects.count() == 2
    assert FakeModel2.objects.count() == 2
    queryset = CustomVisibility().filter_queryset(Node, FakeModel1.objects, None)
    assert queryset.count() == 0
    queryset = CustomVisibility().filter_queryset(CustomNode1, FakeModel1.objects, None)
    assert queryset.count() == 1
    queryset = CustomVisibility().filter_queryset(CustomNode2, FakeModel2.objects, None)
    assert queryset.count() == 1
