import math

import pytest

from caluma.caluma_analytics.simple_table import SimpleTable


@pytest.fixture
def example_analytics(analytics_table, form_and_document, settings):
    settings.META_FIELDS = ["foo"]
    analytics_table.fields.create(data_source="created_at", alias="created_at")
    analytics_table.fields.create(data_source="created_at.quarter", alias="quarter")
    analytics_table.fields.create(data_source="meta.foo", alias="foo")
    analytics_table.fields.create(data_source="status", alias="statuuuuuus")
    analytics_table.fields.create(
        data_source="document[top_form].top_question", alias="from_the_doc"
    )
    return analytics_table


@pytest.fixture
def analytics_cases(form_and_document, case_factory):
    _f, document, _q, _a = form_and_document(use_subform=True)
    for _ in range(3):
        case_factory(meta={"foo": "bar"}, document=document.copy())


@pytest.mark.freeze_time("2021-10-10")
def test_run_analytics_direct(db, snapshot, example_analytics, analytics_cases):
    """Test basic analytics run on simple table.

    * Test that we get *some* results
    * Tests date part extraction
    * Test Meta field extraction
    """

    table = SimpleTable(example_analytics)

    result = table.get_records()

    assert len(result) == 3

    snapshot.assert_match(result)


@pytest.mark.freeze_time("2021-10-10")
@pytest.mark.parametrize("delete_case", [True, False])
@pytest.mark.parametrize("case__meta", [{"foo": "bar"}])
def test_run_analytics_gql(
    db, snapshot, schema_executor, example_analytics, case, delete_case
):
    """Test basic analytics run on simple table.

    * Test that we get *some* results
    * Tests date part extraction
    * Test Meta field extraction
    """
    query = """
        query run ($input: String!) {
          analyticsTable(slug: $input) {
              resultData {
                records {
                  edges {
                    node {
                      edges {
                        node {
                          alias
                          value
                        }
                      }
                    }
                  }
                }
             }
          }
       }
    """

    example_analytics.fields.filter(alias="from_the_doc").delete()

    if delete_case:
        # Test empty output
        case.delete()

    result = schema_executor(query, variable_values={"input": example_analytics.pk})

    assert not result.errors

    if not delete_case:
        # some explicit sanity checks
        records = result.data["analyticsTable"]["resultData"]["records"]["edges"]
        assert len(records) == 1
        first_row = {
            edge["node"]["alias"]: edge["node"]["value"]
            for edge in records[0]["node"]["edges"]
        }

        assert first_row["quarter"] == str(int(math.ceil(case.created_at.month / 3)))
        assert first_row["foo"] == "bar"

    snapshot.assert_match(result.data)


def test_sql_repeatability(
    db,
    example_analytics,
):

    example_analytics.fields.filter(alias="from_the_doc").delete()
    table = SimpleTable(example_analytics)

    sql1, params1 = table.get_sql_and_params()
    sql2, params2 = table.get_sql_and_params()

    assert sql1 == sql2
    assert params1 == params2
