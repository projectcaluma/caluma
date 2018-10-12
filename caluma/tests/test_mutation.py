import pytest
from django.http import Http404
from graphene import ResolveInfo
from rest_framework import serializers

from .. import models, mutation, types
from .fake_model import get_fake_model


@pytest.fixture
def mock_info():
    return ResolveInfo(
        None,
        None,
        None,
        None,
        schema=None,
        fragments=None,
        root_value=None,
        operation=None,
        variable_values=None,
        context=None,
    )


def test_missing_serializer_mutation_serializer_class():
    with pytest.raises(Exception) as exc:

        class MyMutation(mutation.SerializerMutation):
            pass

    assert str(exc.value) == "serializer_class is required for the SerializerMutation"


def test_invalid_serializer_mutation_model_operations(db):
    class MySerializer(serializers.ModelSerializer):
        class Meta:
            model = get_fake_model()
            fields = "__all__"

    with pytest.raises(Exception) as exc:

        class MyMutation(mutation.SerializerMutation):
            class Meta:
                serializer_class = MySerializer
                model_operations = ["Add"]

    assert "model_operations" in str(exc.value)


def test_invalid_serializer_mutation_update_mutate_and_get_payload(db, mock_info):
    class MySerializer(serializers.ModelSerializer):
        class Meta:
            model = get_fake_model()
            fields = "__all__"

    class InvalidModelMutation(mutation.SerializerMutation):
        class Meta:
            serializer_class = MySerializer
            model_operations = ["update"]

    with pytest.raises(Exception) as exc:
        InvalidModelMutation.mutate_and_get_payload(None, mock_info)

    assert '"id" required' in str(exc.value)


def test_serializer_mutation_mutate_and_get_payload_without_model(mock_info):
    class MySerializer(serializers.Serializer):
        name = serializers.CharField()

        def create(self, validated_data):
            return validated_data

    class NoModelMutation(mutation.SerializerMutation):
        class Meta:
            return_field_name = "test"
            serializer_class = MySerializer

    result = NoModelMutation.mutate_and_get_payload(None, mock_info, name="test")
    assert type(result) == NoModelMutation


def test_user_defined_primary_key_get_serializer_kwargs_not_allowed(db, mock_info):
    """Test that user may not overwrite existing instance which is not visible."""
    FakeModel = get_fake_model(model_base=models.SlugModel)

    class FakeModelObjectType(types.DjangoObjectType):
        class Meta:
            model = FakeModel

        @classmethod
        def get_queryset(cls, queryset, info):
            # enforce that nothing is visible
            return queryset.none()

    class MySerializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class MyMutation(mutation.UserDefinedPrimaryKeyMixin, mutation.SerializerMutation):
        class Meta:
            serializer_class = MySerializer
            return_field_type = FakeModelObjectType

    FakeModel.objects.create(slug="test")

    with pytest.raises(Http404):
        MyMutation.get_serializer_kwargs(None, mock_info, slug="test")
