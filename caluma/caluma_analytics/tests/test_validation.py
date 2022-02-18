from graphql_relay import to_global_id

from .. import models

MUTATION_SAVE_FIELD = """
    mutation addfield($input: SaveAnalyticsFieldInput!) {
      saveAnalyticsField(input: $input) {
        analyticsField {
          table {
            name
            fields {
              edges {
                node {
                  alias
                  dataSource
                }
              }
            }
          }
        }
        clientMutationId
      }
    }
"""

MUTATION_SAVE_TABLE = """
    mutation create ($input:SaveAnalyticsTableInput!){
      saveAnalyticsTable(input: $input) {
        clientMutationId
      }
    }
"""


def test_create_table_no_starting_object(db, schema_executor):
    result = schema_executor(
        MUTATION_SAVE_TABLE,
        variable_values={
            "input": {
                "slug": "test-table",
                "name": "Test table thingy",
                "tableType": "TYPE_EXTRACTION",
            }
        },
    )

    assert result.errors
    assert "starting object must be provided for tables with TYPE_EXTRACTION" in str(
        result.errors[0]
    )


def test_save_pivot_field_bad_reference(
    db, schema_executor, example_analytics, analytics_table_factory
):
    pivot_table = analytics_table_factory(
        table_type=models.AnalyticsTable.TYPE_PIVOT, base_table=example_analytics
    )

    result = schema_executor(
        MUTATION_SAVE_FIELD,
        variable_values={
            "input": {
                "alias": "test-table",
                "dataSource": "field_that_does_not_exist",
                "table": pivot_table.slug,
            }
        },
    )

    assert result.errors
    assert (
        "Pivot table field: Data source 'field_that_does_not_exist' must exist in base table"
        in str(result.errors[0])
    )


def test_remove_base_table(db, schema_executor, example_analytics, example_pivot_table):
    query = """
        mutation remove($input: RemoveAnalyticsTableInput!) {
          removeAnalyticsTable(input: $input) {
            clientMutationId
          }
        }
    """

    # base table cannot be deleted
    result = schema_executor(
        query, variable_values={"input": {"slug": example_analytics.pk}}
    )
    assert result.errors

    # delete pivot table
    result = schema_executor(
        query, variable_values={"input": {"slug": example_pivot_table.pk}}
    )
    assert not result.errors

    # now, the base table can be deleted
    result = schema_executor(
        query, variable_values={"input": {"slug": example_analytics.pk}}
    )
    assert not result.errors


def test_remove_referenced_field(
    db, schema_executor, example_analytics, example_pivot_table
):
    query = """
        mutation remove($input: RemoveAnalyticsFieldInput!) {
          removeAnalyticsField(input: $input) {
            clientMutationId
          }
        }
    """

    to_delete_field = example_analytics.fields.get(
        alias=example_pivot_table.fields.first().data_source
    )

    input = {
        "input": {
            "id": to_global_id(type(to_delete_field).__name__, to_delete_field.pk)
        }
    }

    result = schema_executor(query, variable_values=input)
    assert result.errors
    assert f"This field is still referenced in table {example_pivot_table.slug}" in str(
        result.errors[0].args
    )
