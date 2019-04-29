import pytest
from django.core.cache import cache
from django.utils import translation


def test_fetch_data_sources(snapshot, schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.data_source.tests.data_sources.MyDataSource",
        "caluma.data_source.tests.data_sources.MyFaultyDataSource",
        "caluma.data_source.tests.data_sources.MyOtherFaultyDataSource",
    ]
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

    with translation.override("de"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)

    with translation.override("nolang"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)


def test_fetch_data_from_data_source(snapshot, schema_executor, data_source_settings):
    query = """
        query dataSource {
          dataSource (name: "MyDataSource") {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                label
                slug
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert not result.errors
    snapshot.assert_match(result.data)
    assert cache.get("data_source_MyDataSource") == [
        1,
        5.5,
        "sdkj",
        ["value", "info"],
        ["something"],
        [
            "translated_value",
            {"de": "deutsche Beschreibung", "en": "english description"},
        ],
    ]

    with translation.override("de"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)

    with translation.override("nolang"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "data_source", ["MyFaultyDataSource", "MyOtherFaultyDataSource"]
)
def test_data_source_failure(data_source, schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        f"caluma.data_source.tests.data_sources.{data_source}"
    ]

    query = """
        query dataSource($name: String!) {
          dataSource (name: $name) {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                label
                slug
              }
            }
          }
        }
    """

    inp = {"name": data_source}

    result = schema_executor(query, variables=inp)
    assert result.errors


def test_data_source_defaults(snapshot, schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        f"caluma.data_source.tests.data_sources.MyBrokenDataSource"
    ]

    query = """
            query dataSource {
              dataSource (name: "MyBrokenDataSource") {
                pageInfo {
                  startCursor
                  endCursor
                }
                edges {
                  node {
                    label
                    slug
                  }
                }
              }
            }
        """

    result = schema_executor(query, variables={})
    assert not result.errors
    snapshot.assert_match(result.data)


def test_data_source_exception(schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        f"caluma.data_source.tests.data_sources.MyOtherBrokenDataSource"
    ]

    query = """
            query dataSource {
              dataSource (name: "MyOtherBrokenDataSource") {
                pageInfo {
                  startCursor
                  endCursor
                }
                edges {
                  node {
                    label
                    slug
                  }
                }
              }
            }
        """

    result = schema_executor(query, variables={})
    assert result.errors


@pytest.mark.parametrize("configure", [True, False])
def test_fetch_data_from_non_existing_data_source(schema_executor, settings, configure):
    if configure:
        settings.DATA_SOURCE_CLASSES = [
            f"caluma.data_source.tests.data_sources.NonExistentDataSource"
        ]

    query = """
        query dataSource {
          dataSource (name: "NonExistentDataSource") {
            pageInfo {
              startCursor
              endCursor
            }
            edges {
              node {
                label
                slug
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert result.errors
