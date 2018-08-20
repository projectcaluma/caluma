import graphene
from graphene.relay import Node

from .form import schema as form_schema


class Query(form_schema.Query, graphene.ObjectType):
    node = Node.Field()


schema = graphene.Schema(query=Query)
