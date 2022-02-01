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


# The following is a strict copy of the function
# `graphql.language.block_string.print_block_string` with the issue
# fixed that it cannot handle lazy strings coming from django translations.
# TODO: Remove once patched upstream
def _print_block_string(
    value: str, indentation: str = "", prefer_multiple_lines: bool = False
) -> str:
    """Print a block string in the indented block form.

    Prints a block string in the indented block form by adding a leading and
    trailing blank line. However, if a block string starts with whitespace and
    is a single-line, adding a leading blank line would strip that whitespace.

    For internal use only.
    """
    is_single_line = "\n" not in value
    has_leading_space = value.startswith(" ") or value.startswith("\t")
    has_trailing_quote = value.endswith('"')
    has_trailing_slash = value.endswith("\\")
    print_as_multiple_lines = (
        not is_single_line
        or has_trailing_quote
        or has_trailing_slash
        or prefer_multiple_lines
    )

    # Format a multi-line block quote to account for leading space.
    if print_as_multiple_lines and not (is_single_line and has_leading_space):
        result = "\n" + indentation
    else:
        result = ""

    # str(value) is required, as value might also be a lazy object
    result += value.replace("\n", "\n" + indentation) if indentation else str(value)
    if print_as_multiple_lines:
        result += "\n"

    return '"""' + result.replace('"""', '\\"""') + '"""'


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
    # This is the old test for checking the schema.
    # It is currently expected to fail, as graphql has a bug preventing
    # it from working.
    # Once this start XFAILing, remove the above patchy version and
    # remove the xfail flag here

    _sort_schema_typemap()
    snapshot.assert_match(str(schema))
