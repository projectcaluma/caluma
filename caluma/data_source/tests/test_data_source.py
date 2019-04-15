import pytest
from django.core.cache import cache

from caluma.data_source.data_sources import BaseDataSource


def test_fetch_data_sources(snapshot, schema_executor, data_source_mock):
    query = """
        query dataSources {
          allDataSources {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                name
                info
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert not result.errors
    snapshot.assert_match(result.data)


def test_fetch_data_from_data_source(snapshot, schema_executor, data_source_mock):
    query = """
        query dataSource {
          dataSource (name: "MyDataSource") {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                option
                value
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert not result.errors
    snapshot.assert_match(result.data)
    assert cache.get("data_source_MyDataSource_None")["data"] == [
        1,
        5.5,
        "sdkj",
        ["info", "value"],
        ["something"],
    ]


@pytest.mark.parametrize("data", ["just a string", [["just", "some", "strings"]]])
def test_fetch_faulty_data_from_data_source(data, schema_executor, data_source_mock):
    class MyFaultyDataSource(BaseDataSource):
        info = "Nice test data source"
        timeout = 3600
        default = []

        def get_data(self, info):
            return data

    data_source_mock.MyFaultyDataSource = MyFaultyDataSource

    query = """
        query dataSource {
          dataSource (name: "MyFaultyDataSource") {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                option
                value
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert result.errors


def test_fetch_data_from_non_existing_data_source(schema_executor,):
    query = """
        query dataSource {
          dataSource (name: "NonExistentDataSource") {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                option
                value
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert result.errors
