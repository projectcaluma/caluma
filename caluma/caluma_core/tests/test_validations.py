import pytest
from django.core.exceptions import ImproperlyConfigured

from .. import models, mutation, serializers, types, validations
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


def test_custom_validation_override_created_by_group(db, admin_info, history_mock):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class CustomValidation(validations.BaseValidation):
        def validate(self, mutation, data, info):
            info.context.user.group = "foobar"
            return data

    class MySerializer(serializers.ModelSerializer):
        validation_classes = [CustomValidation]

        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomNode(types.DjangoObjectType):
        class Meta:
            model = FakeModel

    class MyMutation(mutation.Mutation):
        class Meta:
            serializer_class = MySerializer

    MyMutation.mutate_and_get_payload(None, admin_info)
    assert FakeModel.objects.first().created_by_group == "foobar"


def test_custom_validation_chained_decorators(db, info):
    FakeModel = get_fake_model(model_base=models.UUIDModel)

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = FakeModel
            fields = "__all__"

    class CustomMutation1(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomMutation2(Mutation):
        class Meta:
            serializer_class = Serializer

    class CustomValidation(BaseValidation):
        @validation_for(CustomMutation1)
        @validation_for(CustomMutation2)
        def validate_custom_mutation(self, mutation, data, info):
            data["test"] = "test"
            return data

    data = CustomValidation().validate(CustomMutation1, {}, info)
    assert data["test"] == "test"

    data = CustomValidation().validate(CustomMutation2, {}, info)
    assert data["test"] == "test"
