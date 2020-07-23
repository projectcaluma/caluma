import pytest
from django.core.cache import cache
from django.utils import translation

from caluma.caluma_form.models import DynamicOption, Question
from caluma.caluma_user.models import BaseUser


def test_fetch_data_sources(snapshot, schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource",
        "caluma.caluma_data_source.tests.data_sources.MyFaultyDataSource",
        "caluma.caluma_data_source.tests.data_sources.MyOtherFaultyDataSource",
    ]
    query = """
        query dataSources {
          allDataSources {
            totalCount
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
            totalCount
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
        (5.5,),
        "sdkj",
        ("value", "info"),
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
        f"caluma.caluma_data_source.tests.data_sources.{data_source}"
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

    result = schema_executor(query, variable_values=inp)
    assert result.errors


def test_data_source_defaults(snapshot, schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyBrokenDataSource"
    ]

    query = """
            query dataSource {
              dataSource (name: "MyBrokenDataSource") {
                totalCount
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

    result = schema_executor(query, variable_values={})
    assert not result.errors
    snapshot.assert_match(result.data)


def test_data_source_exception(schema_executor, settings):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyOtherBrokenDataSource"
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

    result = schema_executor(query, variable_values={})
    assert result.errors


@pytest.mark.parametrize("configure", [True, False])
def test_fetch_data_from_non_existing_data_source(schema_executor, settings, configure):
    if configure:
        settings.DATA_SOURCE_CLASSES = [
            "caluma.caluma_data_source.tests.data_sources.NonExistentDataSource"
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


@pytest.mark.parametrize(
    "question__type,question__data_source",
    [(Question.TYPE_DYNAMIC_CHOICE, "MyDataSource")],
)
def test_data_sources_stores_user(
    db, schema_executor, info, settings, form, question, document
):
    class FakeUser(BaseUser):
        def __init__(self):
            self.groups = ["foobar"]
            self.username = "asdf"

        @property
        def group(self):
            return "foobar"

        def __str__(self):
            return "asdf"

    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSource"
    ]
    query = """
      mutation createAnswer($input:SaveDocumentStringAnswerInput!){
        saveDocumentStringAnswer(input:$input){
          answer{
            id
          }
        }
      }
    """
    info.context.user = FakeUser()
    variables = {
        "input": {
            "question": question.slug,
            "document": str(document.id),
            "value": "something",
        }
    }
    assert not DynamicOption.objects.exists()
    result = schema_executor(query, variable_values=variables, info=info)
    assert not result.errors
    assert DynamicOption.objects.filter(
        document=document,
        question=question,
        slug="something",
        created_by_user="asdf",
        created_by_group="foobar",
    ).exists()
