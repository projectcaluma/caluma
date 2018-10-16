import graphene
from django.utils import translation
from graphene_django.converter import convert_django_field_with_choices
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework import serializer_converter
from graphql_relay import to_global_id
from localized_fields.fields import LocalizedField
from rest_framework import relations, serializers

from . import validators
from .relay import extract_global_id


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
        self.validators.append(validators.JexlValidator(jexl))


class ModelSerializer(serializers.ModelSerializer):
    serializer_related_field = GlobalIDPrimaryKeyRelatedField

    def build_standard_field(self, field_name, model_field):
        field_class, field_kwargs = super().build_standard_field(
            field_name, model_field
        )

        if isinstance(model_field, LocalizedField):
            lang = translation.get_language()
            allow_blank = model_field.blank or lang not in model_field.required
            field_kwargs["allow_blank"] = allow_blank

        return field_class, field_kwargs


ModelSerializer.serializer_field_mapping.update({LocalizedField: serializers.CharField})


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
