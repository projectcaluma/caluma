import graphene
from graphene_django.converter import convert_django_field_with_choices
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework import serializer_converter
from graphql_relay import to_global_id
from localized_fields.fields import LocalizedField
from rest_framework import relations, serializers

from .relay import extract_global_id


class GlobalIDPrimaryKeyRelatedField(relations.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        data = extract_global_id(data)
        return super().to_internal_value(data)

    def to_representation(self, value):
        value = super().to_representation(value)
        return to_global_id(self.get_queryset().model.__name__, value)


class GlobalIDField(serializers.Field):
    def to_internal_value(self, data):
        return extract_global_id(data)


class ModelSerializer(serializers.ModelSerializer):
    serializer_related_field = GlobalIDPrimaryKeyRelatedField


serializers.ModelSerializer.serializer_field_mapping.update(
    {LocalizedField: serializers.CharField}
)


@serializer_converter.get_graphene_type_from_serializer_field.register(
    relations.RelatedField
)
@serializer_converter.get_graphene_type_from_serializer_field.register(GlobalIDField)
def convert_serializer_relation_to_id(field):
    return graphene.ID


@serializer_converter.get_graphene_type_from_serializer_field.register(
    serializers.ChoiceField
)
def convert_serializer_field_to_enum(field):
    # TODO: could be removed once following issue is fixed
    # https://github.com/graphql-python/graphene-django/issues/517
    model_class = None
    serializer_meta = getattr(field.parent, "Meta", None)
    if serializer_meta:
        model_class = getattr(serializer_meta, "model", None)

    if model_class:
        registry = get_global_registry()
        model_field = model_class._meta.get_field(field.source)
        return type(convert_django_field_with_choices(model_field, registry))

    return graphene.String
