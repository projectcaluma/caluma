import pytest

from caluma.caluma_analytics.pivot_table import PivotTable


def _table_output_to_rows(output):
    """Convert GQL output (list of list of gql dicts) into simple list of dicts."""
    return [
        {col["node"]["alias"]: col["node"]["value"] for col in rec["node"]["edges"]}
        for rec in output
    ]


@pytest.mark.freeze_time("2021-10-10")
def test_run_analytics_direct(db, snapshot, example_pivot_table, analytics_cases):
    """Test basic analytics run on simple table.

    * Test that we get *some* results
    * Tests date part extraction
    * Test Meta field extraction
    """

    table = PivotTable(example_pivot_table)

    result = table.get_records()

    assert len(result) == 3

    snapshot.assert_match(sorted(result, key=lambda r: r["status"]))


@pytest.mark.freeze_time("2021-10-10")
@pytest.mark.parametrize("delete_case", [True, False])
@pytest.mark.parametrize("case__meta", [{"foo": "bar"}])
def test_run_analytics_gql(
    db,
    schema_executor,
    example_pivot_table,
    case,
    delete_case,
    analytics_cases,
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
                summary {
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
    """

    if delete_case:
        # Test empty output
        case.delete()

    result = schema_executor(query, variable_values={"input": example_pivot_table.pk})
    assert not result.errors

    if not delete_case:
        # some explicit sanity checks
        records = result.data["analyticsTable"]["resultData"]["records"]["edges"]
        assert len(records) == 3
        data = _table_output_to_rows(records)
        created_by_status = {row["status"]: row["last_created"] for row in data}

        assert created_by_status == {
            "running": "2022-02-03 00:00:00+00:00",
            "completed": "2022-02-04 00:00:00+00:00",
            "suspended": "2022-02-05 00:00:00+00:00",
        }

        summary = result.data["analyticsTable"]["resultData"]["summary"]["edges"]

        summary_dict = {col["node"]["alias"]: col["node"]["value"] for col in summary}
        assert summary_dict == {
            "last_created": "2022-02-05 00:00:00+00:00",
            "quarter": "4",
        }
