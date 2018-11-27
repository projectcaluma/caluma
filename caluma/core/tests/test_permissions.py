import pytest
from rest_framework import serializers

from .. import models
from ..mutation import Mutation
from ..permissions import BasePermission, object_permission_for, permission_for
from .fake_model import get_fake_model


def test_custom_permission_override_has_permission_for_custom_node(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)
    instance = FakeModel.objects.create()

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomPermission(BasePermission):
        @permission_for(CustomMutation)
        def has_permission_for_custom_mutation(self, mutation, info):
            return False

        @object_permission_for(CustomMutation)
        def has_object_permission_for_custom_mutation(self, mutation, info, instance):
            return False

    assert not CustomPermission().has_permission(CustomMutation, info)
    assert not CustomPermission().has_object_permission(CustomMutation, info, instance)


def test_custom_permission_override_has_permission_with_duplicates(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomPermission(BasePermission):
        @permission_for(CustomMutation)
        def has_permission_for_custom_mutation(
            self, mutation, info
        ):  # pragma: no cover
            return False

        @permission_for(CustomMutation)
        def has_permission_for_custom_mutation_2(
            self, mutation, info
        ):  # pragma: no cover
            return False

    with pytest.raises(AssertionError):
        CustomPermission()


def test_custom_permission_override_has_object_permission_with_duplicates(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomPermission(BasePermission):
        @object_permission_for(CustomMutation)
        def has_object_permission_for_custom_mutation(
            self, mutation, info, instance
        ):  # pragma: no cover
            return False

        @object_permission_for(CustomMutation)
        def has_object_permission_for_custom_mutation_2(
            self, mutation, info, instance
        ):  # pragma: no cover
            return False

    with pytest.raises(AssertionError):
        CustomPermission()
