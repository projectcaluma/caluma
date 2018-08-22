import graphene
from graphene.relay import Node

from .form import schema as form_schema


class Mutation(form_schema.Mutation, graphene.ObjectType):
    pass


class Query(form_schema.Query, graphene.ObjectType):
    node = Node.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
