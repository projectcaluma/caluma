import pytest
from django.core.exceptions import ImproperlyConfigured

from .. import models, serializers
from ..mutation import Mutation
from ..validations import BaseValidation, validation_for
from .fake_model import get_fake_model


def test_custom_validation_override_validate_custom_node(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomValidation(BaseValidation):
        @validation_for(CustomMutation)
        def validate_custom_mutation(self, mutation, data, info):
            data["test"] = "test"
            return data

    data = CustomValidation().validate(CustomMutation, {}, info)
    assert data["test"] == "test"


def test_custom_validation_override_validate_with_duplicates(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomValidation(BaseValidation):
        @validation_for(CustomMutation)
        def validate_custom_mutation(self, mutation, data, info):  # pragma: no cover
            return data

        @validation_for(CustomMutation)
        def validate_custom_mutation_2(self, mutation, data, info):  # pragma: no cover
            return data

    with pytest.raises(ImproperlyConfigured):
        CustomValidation()


def test_custom_validation_override_validate_no_class_match(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class AnotherMutation(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomValidation(BaseValidation):
        @validation_for(CustomMutation)
        def validate_custom_mutation(self, mutation, data, info):  # pragma: no cover
            return data

    assert CustomValidation().validate(AnotherMutation, {}, info) == {}
