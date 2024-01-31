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
    """ % {"name": node_instance.__class__.__name__}

    result = schema.execute(node_query, variable_values={"id": global_id})
    assert not result.errors
    assert result.data["node"]["id"] == global_id


def _sort_schema_typemap():
    """Make the schema's typemap sorted.

    This is required for our schema snapshot test,
    which we want to be as comparable as possible, so
    changes can be detected.
    In graphene before 3.0, this was implicitly the case,
    but 3.0 changed this, so we're monkeypatching
    a sorted version here.

    This has no functional impact except on the schema
    dump in the snapshots.
    """
    type_map = schema.graphql_schema.type_map
    schema.graphql_schema.type_map = {k: type_map[k] for k in sorted(type_map.keys())}


def test_schema_introspect_direct(snapshot):
    _sort_schema_typemap()
    snapshot.assert_match(str(schema))
