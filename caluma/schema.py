import graphene
from django.conf import settings
from graphene.relay import Node
from graphene_django.converter import convert_django_field, convert_field_to_string
from graphene_django.debug import DjangoDebug
from localized_fields.fields import LocalizedField

from .data_source import schema as data_source_schema
from .form import historical_schema as form_historical_schema, schema as form_schema
from .workflow import schema as workflow_schema

convert_django_field.register(LocalizedField, convert_field_to_string)


class Mutation(form_schema.Mutation, workflow_schema.Mutation, graphene.ObjectType):
    pass


class Query(
    form_schema.Query,
    form_historical_schema.Query,
    workflow_schema.Query,
    data_source_schema.Query,
    graphene.ObjectType,
):
    node = Node.Field()
    if settings.DEBUG:
        debug = graphene.Field(DjangoDebug, name="_debug")


schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    # TODO: define what app exposes what types
    types=[
        form_schema.TextQuestion,
        form_schema.ChoiceQuestion,
        form_schema.MultipleChoiceQuestion,
        form_schema.DynamicChoiceQuestion,
        form_schema.DynamicMultipleChoiceQuestion,
        form_schema.TextareaQuestion,
        form_schema.FloatQuestion,
        form_schema.IntegerQuestion,
        form_schema.DateQuestion,
        form_schema.TableQuestion,
        form_schema.FormQuestion,
        form_schema.FileQuestion,
        form_schema.StaticQuestion,
        form_schema.StringAnswer,
        form_schema.ListAnswer,
        form_schema.IntegerAnswer,
        form_schema.FloatAnswer,
        form_schema.DateAnswer,
        form_schema.TableAnswer,
        form_schema.FileAnswer,
        form_historical_schema.HistoricalStringAnswer,
        form_historical_schema.HistoricalListAnswer,
        form_historical_schema.HistoricalIntegerAnswer,
        form_historical_schema.HistoricalFloatAnswer,
        form_historical_schema.HistoricalDateAnswer,
        form_historical_schema.HistoricalTableAnswer,
        form_historical_schema.HistoricalFileAnswer,
        workflow_schema.SimpleTask,
        workflow_schema.CompleteWorkflowFormTask,
        workflow_schema.CompleteTaskFormTask,
    ],
)
