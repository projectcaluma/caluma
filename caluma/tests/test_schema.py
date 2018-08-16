import glob
import os

import pytest
from graphql_relay import to_global_id

from ..schema import schema

DIR_NAME = os.path.dirname(__file__)


def schema_query_files():
    """Get schema query files for testing.

    As this is written into a snapshot only extract relative path.
    """

    query_files = glob.glob(os.path.join(DIR_NAME, "queries/*.graphql"))

    return [os.path.join(*query_file.split(os.sep)[-2:]) for query_file in query_files]


@pytest.mark.parametrize("query_file", schema_query_files())
def test_schema_queries(db, form, snapshot, query_file):
    """Add your graphql test file to queries folder for automatic testing."""

    with open(os.path.join(DIR_NAME, query_file)) as query:
        result = schema.execute(query.read())
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("node_type", ["form"])
def test_schema_node(db, snapshot, request, node_type):
    """
    Add your model to parametrize for automatic global node testing.

    Requirement is that node and model have the same name
    """
    node_instance = request.getfixturevalue(node_type)
    global_id = to_global_id(node_instance.__class__.__name__, node_instance.pk)

    node_query = """
    query %(name)s($id: ID!) {
      node(id: $id) {
        ... on %(name)s {
          id
        }
      }
    }
    """ % {
        "name": node_instance.__class__.__name__
    }

    result = schema.execute(node_query, variables={"id": global_id})
    assert not result.errors
    assert result.data["node"]["id"] == global_id
