import graphene

from .form import schema as form_schema


class Query(form_schema.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
