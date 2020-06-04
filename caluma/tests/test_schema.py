import os

import pytest
from graphql_relay import to_global_id

from ..schema import schema

DIR_NAME = os.path.dirname(__file__)


@pytest.mark.parametrize("node_type", ["form", "workflow"])
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

    result = schema.execute(node_query, variable_values={"id": global_id})
    assert not result.errors
    assert result.data["node"]["id"] == global_id


def test_schema_introspect(snapshot):
    snapshot.assert_match(str(schema))
