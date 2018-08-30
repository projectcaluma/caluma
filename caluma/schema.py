import graphene
from graphene.relay import Node
from graphene_django.converter import convert_django_field, convert_field_to_string
from localized_fields.fields import LocalizedField

from .form import schema as form_schema

convert_django_field.register(LocalizedField, convert_field_to_string)


class Mutation(form_schema.Mutation, graphene.ObjectType):
    pass


class Query(form_schema.Query, graphene.ObjectType):
    node = Node.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
