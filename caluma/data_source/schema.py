from graphene import Connection, ConnectionField, String
from graphene.types import ObjectType

from .data_source_handlers import get_data_source_data, get_data_sources


class DataSource(ObjectType):
    info = String()
    name = String(required=True)


class DataSourceConnection(Connection):
    class Meta:
        node = DataSource


class DataSourceData(ObjectType):
    label = String(required=True)
    slug = String(required=True)


class DataSourceDataConnection(Connection):
    class Meta:
        node = DataSourceData


class Query(object):
    all_data_sources = ConnectionField(DataSourceConnection)
    data_source = ConnectionField(DataSourceDataConnection, name=String())

    def resolve_all_data_sources(self, info):
        return get_data_sources()

    def resolve_data_source(self, info, name):
        return get_data_source_data(info, name)
