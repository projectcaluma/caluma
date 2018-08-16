import glob
import os

import pytest

from ..schema import schema

DIR_NAME = os.path.dirname(__file__)


def schema_query_files():
    """Get schema query files for testing.

    As this is written into a snapshot only extract relative path.
    """

    query_files = glob.glob(os.path.join(DIR_NAME, "queries/*.graphql"))

    return [os.path.join(*query_file.split(os.sep)[-2:]) for query_file in query_files]


@pytest.mark.parametrize("query_file", schema_query_files())
def test_schema(db, form, snapshot, query_file):
    """Add your graphql test file to queries folder for automatic testing."""

    with open(os.path.join(DIR_NAME, query_file)) as query:
        result = schema.execute(query.read())
    assert not result.errors
    snapshot.assert_match(result.data)
