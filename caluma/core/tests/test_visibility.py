import pytest
from django.core.exceptions import ImproperlyConfigured
from django.db.models import CharField

from .. import models
from ...form.schema import Form
from ..types import DjangoObjectType, Node
from ..visibilities import BaseVisibility, Union, filter_queryset_for
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


def test_custom_visibility_override_specificity(db):
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


def test_union_visibility(db):
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


def test_union_visibility_none(db):
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


def test_has_answer_filter(
    db, form, form_question, question, schema_executor, answer_factory, document
):

    # verify assumptions
    assert question in form.questions.all()

    answer1 = answer_factory(question=question)
    answer2 = answer_factory(question=question)

    # need two different documents (verifying more assumptions)
    assert answer1.document.id != answer2.document.id

    query = """
        query blub($hasAnswer: String) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                id
              }
            }
          }
        }
    """
    result = schema_executor(
        query, variables={"hasAnswer": f"{question.slug}={answer1.value}"}
    )
    assert not result.errors
    assert len(result.data["allDocuments"]["edges"]) == 1
