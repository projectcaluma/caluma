import enum

import graphene
from django.core.exceptions import ImproperlyConfigured
from django.utils import translation
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework import serializer_converter
from graphql_relay import to_global_id
from localized_fields.fields import LocalizedField
from rest_framework import relations, serializers
from rest_framework.serializers import ChoiceField

from .jexl import JexlValidator
from .relay import extract_global_id


class CalumaChoiceField(ChoiceField):
    """Custom choice field.

    Correctly handles Enum values that graphene parses before the
    value gets to the DRF serializer.
    """

    def to_internal_value(self, data):
        # TODO: This shouldn't be required IMHO - find out why
        # graphene parses the enum value before we get to it
        #
        # This is a workaround for the following bug:
        # https://github.com/graphql-python/graphene-django/issues/1280
        #
        # If/when this bug is fixed, this whole intermediate class may
        # become obsolete
        if isinstance(data, enum.Enum):
            data = data.value
        return super().to_internal_value(data)


class GlobalIDPrimaryKeyRelatedField(relations.PrimaryKeyRelatedField):
    """
    References a global id primary key.

    This class ensures that only primary keys may be looked up which are visible
    by corresponding DjangoObjectType.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        registry = get_global_registry()
        node_type = registry.get_type_for_model(queryset.model)
        return node_type.get_queryset(queryset, self.context.get("info"))

    def to_internal_value(self, data):
        data = extract_global_id(data)
        return super().to_internal_value(data)

    def to_representation(self, value):
        value = super().to_representation(value)
        return to_global_id(self.get_queryset().model.__name__, value)


class GlobalIDField(serializers.Field):
    def to_internal_value(self, data):
        return extract_global_id(data)


class JexlField(serializers.CharField):
    def __init__(self, jexl, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(JexlValidator(jexl))


class ModelSerializer(serializers.ModelSerializer):
    serializer_related_field = GlobalIDPrimaryKeyRelatedField
    serializer_field_mapping = {
        **serializers.ModelSerializer.serializer_field_mapping,
        LocalizedField: serializers.CharField,
    }

    # will be set in caluma_core.AppConfig.ready hook, see apps.py
    # to avoid recursive import error
    validation_classes = None

    def validate(self, data):
        mutation = self.context["mutation"]
        info = self.context["info"]

        if self.validation_classes is None:
            raise ImproperlyConfigured(
                "check that app `caluma.caluma_core` is part of your `INSTALLED_APPS` "
                "or custom mutation has `validation_classes` properly assigned."
            )

        for validation_class in self.validation_classes:
            data = validation_class().validate(mutation, data, info)

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["created_by_user"] = user.username
        validated_data["created_by_group"] = user.group

        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["modified_by_user"] = user.username
        validated_data["modified_by_group"] = user.group

        return super().update(instance, validated_data)

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )

        if isinstance(model_field, LocalizedField):
            lang = translation.get_language()
            allow_blank = model_field.blank or lang not in model_field.required
            field_kwargs["allow_blank"] = allow_blank

        return field_class, field_kwargs


@serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.ManyRelatedField
)
def convert_serializer_primary_key_related_field(field):
    return (graphene.List, graphene.ID)


@serializer_converter.get_graphene_type_from_serializer_field.register(
    relations.RelatedField
)
@serializer_converter.get_graphene_type_from_serializer_field.register(GlobalIDField)
def convert_serializer_relation_to_id(field):
    # TODO: could be removed once following issue is fixed
    # https://github.com/graphql-python/graphene-django/issues/389
    return graphene.ID
