import pytest
from django.http import Http404
from rest_framework import exceptions, serializers

from .. import models, mutation, permissions, types
from .fake_model import get_fake_model


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


def test_invalid_serializer_mutation_update_mutate_and_get_payload(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class FakeModelObjectType(types.DjangoObjectType):
        class Meta:
            model = FakeModel

        @classmethod
        def get_queryset(cls, queryset, info):
            # enforce that nothing is visible
            return queryset.none()

    class MySerializer(serializers.ModelSerializer):
        class Meta:
            model = get_fake_model()
            fields = "__all__"

    class InvalidModelMutation(mutation.SerializerMutation):
        class Meta:
            serializer_class = MySerializer
            return_field_type = FakeModelObjectType
            model_operations = ["update"]

    with pytest.raises(Exception) as exc:
        InvalidModelMutation.mutate_and_get_payload(None, info)

    assert '"id" required' in str(exc.value)


def test_serializer_mutation_mutate_and_get_payload_without_model(info):
    class MySerializer(serializers.Serializer):
        name = serializers.CharField()

        def create(self, validated_data):
            return validated_data

    class NoModelMutation(mutation.SerializerMutation):
        class Meta:
            return_field_name = "test"
            serializer_class = MySerializer

    result = NoModelMutation.mutate_and_get_payload(None, info, name="test")
    assert type(result) == NoModelMutation


def test_serializer_mutation_mutate_and_get_payload_without_permission(
    db, settings, info
):
    class MySerializer(serializers.ModelSerializer):
        class Meta:
            model = get_fake_model()
            fields = "__all__"

    class MyMutation(mutation.SerializerMutation):
        class Meta:
            serializer_class = MySerializer

    class NoPermission(permissions.BasePermission):
        def has_permission(self, mutation, info):
            return False

    settings.PERMISSION_CLASSES = [NoPermission]

    with pytest.raises(exceptions.PermissionDenied):
        MyMutation.mutate_and_get_payload(None, info)


def test_serializer_mutation_mutate_and_get_payload_without_object_permission(
    db, settings, info
):
    FakeModel = get_fake_model()
    instance = FakeModel.objects.create()

    class FakeModelObjectType(types.DjangoObjectType):
        class Meta:
            model = FakeModel

    class MySerializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class MyMutation(mutation.SerializerMutation):
        class Meta:
            serializer_class = MySerializer
            return_field_type = FakeModelObjectType

    class NoObjectPermission(permissions.BasePermission):
        def has_object_permission(self, mutation, info, instance):
            return False

    settings.PERMISSION_CLASSES = [NoObjectPermission]

    with pytest.raises(exceptions.PermissionDenied):
        MyMutation.mutate_and_get_payload(None, info, id=str(instance.pk))


def test_user_defined_primary_key_get_serializer_kwargs_not_allowed(db, info):
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
        MyMutation.get_serializer_kwargs(None, info, slug="test")
