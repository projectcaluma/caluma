from graphene import ConnectionField, JSONString, String
from graphene.types import ObjectType

from ..caluma_core.types import CountableConnectionBase
from ..caluma_form.models import Question
from .data_source_handlers import get_data_source_data, get_data_sources


class DataSource(ObjectType):
    info = String()
    name = String(required=True)


class DataSourceConnection(CountableConnectionBase):
    class Meta:
        node = DataSource


class DataSourceData(ObjectType):
    label = String(required=True)
    slug = String(required=True)


class DataSourceDataConnection(CountableConnectionBase):
    class Meta:
        node = DataSourceData


class Query(ObjectType):
    all_data_sources = ConnectionField(DataSourceConnection)
    data_source = ConnectionField(
        DataSourceDataConnection,
        name=String(required=True),
        question=String(
            description="Slug of the question passed as context to the data source"
        ),
        context=JSONString(
            description="JSON object passed as context to the data source"
        ),
    )

    def resolve_all_data_sources(self, info, **kwargs):
        return get_data_sources()

    def resolve_data_source(self, info, name, question=None, context=None, **kwargs):
        if question:
            question = Question.objects.get(pk=question)

        return get_data_source_data(info.context.user, name, question, context)
