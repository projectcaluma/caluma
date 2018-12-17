import graphene
from graphene.relay import Node
from graphene_django.converter import convert_django_field, convert_field_to_string
from localized_fields.fields import LocalizedField

from .form import schema as form_schema
from .workflow import schema as workflow_schema

convert_django_field.register(LocalizedField, convert_field_to_string)


class Mutation(form_schema.Mutation, workflow_schema.Mutation, graphene.ObjectType):
    pass


class Query(form_schema.Query, workflow_schema.Query, graphene.ObjectType):
    node = Node.Field()


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    # TODO: define what app exposes what types
    types=[
        form_schema.TextQuestion,
        form_schema.RadioQuestion,
        form_schema.CheckboxQuestion,
        form_schema.TextareaQuestion,
        form_schema.FloatQuestion,
        form_schema.IntegerQuestion,
        form_schema.StringAnswer,
        form_schema.ListAnswer,
        form_schema.IntegerAnswer,
        form_schema.FloatAnswer,
        workflow_schema.SimpleTask,
        workflow_schema.CompleteWorkflowFormTask,
    ],
)
