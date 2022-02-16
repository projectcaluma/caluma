import pytest
from graphql_relay import to_global_id

from caluma.caluma_workflow.models import Case

from .. import models
from ..simple_table import CaseStartingObject

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
    mutation create {
      saveAnalyticsTable(input: {
        slug: "test-table",
        name: "Test table thingy",
        startingObject: CASES
      }) {
        analyticsTable {
          name
          availableFields(depth: 1) {
            edges {
              node {
                sourcePath,
                label,
                isLeaf
              }
            }
          }
        }
      }
    }
"""

QUERY_AVAILABLE_FIELDS = """
    query foo ($table: String!, $prefix: String, $depth: Int) {
      analyticsTable(slug: $table) {
        availableFields(prefix: $prefix, depth: $depth){
          edges {
            node {
              id,
              sourcePath,
              label,
              isLeaf
            }
          }
        }
      }
    }
"""


def test_create_table(db, snapshot, schema_executor):
    result = schema_executor(MUTATION_SAVE_TABLE, variable_values={})
    breakpoint()
    assert not result.errors
    assert models.AnalyticsTable.objects.filter(pk="test-table").exists()

    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "prefix,depth",
    [
        (None, None),
        ("meta", 1),
        ("created_at", 1),
        ("created_at", 2),
        ("created_at.year", 1),
    ],
)
def test_available_fields(
    db, analytics_table, schema_executor, snapshot, prefix, depth
):

    variables = {"table": analytics_table.pk}

    if prefix:
        variables["prefix"] = prefix
    if depth:
        variables["depth"] = depth

    result = schema_executor(QUERY_AVAILABLE_FIELDS, variable_values=variables)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "field_path, expect_error",
    [
        ("created_at.quarter", False),
        ("meta.foobar", False),
        ("invalid_field", True),
    ],
)
def test_add_field(
    db,
    snapshot,
    settings,
    schema_executor,
    expect_error,
    field_path,
    analytics_table,
):
    settings.META_FIELDS = ["foobar", "baz"]
    input = {
        "input": {
            "alias": "some_alias",
            "table": analytics_table.slug,
            "dataSource": field_path,
        }
    }

    result = schema_executor(MUTATION_SAVE_FIELD, variable_values=input)

    assert bool(result.errors) == expect_error
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "field_path, field_alias, expect_error, error_key",
    [
        ("created_at.quarter", "quarter", None, None),
        ("meta.baz", "foobar", None, None),
        (
            "meta.foobar",
            "foobar",
            "Cannot use the same data source twice within the same table",
            "dataSource",
        ),
        (
            "meta.foobar",
            "existing",
            "Cannot use the same alias twice within the same table",
            "alias",
        ),
        (
            "invalid_field",
            "foo",
            "Specified data source 'invalid_field' is not available",
            "dataSource",
        ),
    ],
)
def test_add_field_validations(
    db,
    snapshot,
    settings,
    schema_executor,
    field_path,
    field_alias,
    expect_error,
    error_key,
    analytics_table,
):
    settings.META_FIELDS = ["foobar", "baz"]

    analytics_table.fields.create(alias="existing", data_source="meta.foobar")

    input = {
        "input": {
            "alias": field_alias,
            "table": analytics_table.slug,
            "dataSource": field_path,
        }
    }

    result = schema_executor(MUTATION_SAVE_FIELD, variable_values=input)

    assert bool(result.errors) == bool(expect_error)
    if expect_error:
        err = str(result.errors[0].original_error.args[0][error_key][0])
        assert err == expect_error

    snapshot.assert_match(result.data)


def test_update_field(
    db,
    snapshot,
    settings,
    schema_executor,
    analytics_table,
):
    settings.META_FIELDS = ["foobar", "baz"]

    field = analytics_table.fields.create(alias="existing", data_source="meta.foobar")

    input = {
        "input": {
            "alias": field.alias + "_new_alias",
            "table": analytics_table.slug,
            "dataSource": field.data_source,
            "id": str(field.pk),
        }
    }

    result = schema_executor(MUTATION_SAVE_FIELD, variable_values=input)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_remove_field(db, schema_executor, analytics_field):
    query = """
        mutation remove($input: RemoveAnalyticsFieldInput!) {
          removeAnalyticsField(input: $input) {
            analyticsField {
              id
            }
          }
        }
    """

    input = {
        "input": {
            "id": to_global_id(type(analytics_field).__name__, analytics_field.pk)
        }
    }

    result = schema_executor(query, variable_values=input)
    assert not result.errors

    # Try to delete a now-nonexistent field
    result = schema_executor(query, variable_values=input)
    assert result.errors
    assert result.errors[0].args == ("No AnalyticsField matches the given query.",)


def test_remove_table(db, schema_executor, analytics_table):
    query = """
        mutation remove($input: RemoveAnalyticsTableInput!) {
          removeAnalyticsTable(input: $input) {
            analyticsTable {
              id
            }
          }
        }
    """

    input = {"input": {"slug": analytics_table.pk}}

    result = schema_executor(query, variable_values=input)
    assert not result.errors

    # Try to delete a now-nonexistent table
    result = schema_executor(query, variable_values=input)
    assert result.errors
    assert result.errors[0].args == ("No AnalyticsTable matches the given query.",)


@pytest.mark.parametrize("use_gql", [True, False])
def test_full_field_list(
    db,
    settings,
    snapshot,
    schema_executor,
    form_and_document,
    info,
    case,
    work_item_factory,
    task,
    form_question_factory,
    analytics_table,
    use_gql,
):
    form, document, questions, answers_dict = form_and_document(True, True)

    case.document = document
    case.save()
    Case.objects.all().exclude(pk=case.pk).delete()

    # We need some workitems, so we can generate the corresponding
    # fields
    work_item_factory(
        case=case,
        task=task,
        created_at="2021-10-10T00:00:00+02:00",
        closed_at="2021-11-10T00:00:00+01:00",
        child_case=None,
    )

    if use_gql:
        variables = {"table": analytics_table.pk, "prefix": None, "depth": 100}
        result = schema_executor(QUERY_AVAILABLE_FIELDS, variable_values=variables)

        assert not result.errors
        snapshot.assert_match(result.data)

    else:
        start = CaseStartingObject(info, disable_visibilities=False)
        fields = start.get_fields(depth=100)
        snapshot.assert_match(fields)
