import pytest

from .. import models, serializers
from ...schema import schema
from ...tests import extract_serializer_input_fields


def test_save_option(db, option, snapshot):
    query = """
        mutation SaveOption($input: SaveOptionInput!) {
          saveOption(input: $input) {
            option {
              slug
              label
            }
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveOptionSerializer, option
        )
    }

    result = schema.execute(query, variables=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


def test_remove_option(db, option):
    query = """
        mutation RemoveOption($input: RemoveOptionInput!) {
          removeOption(input: $input) {
            clientMutationId
          }
        }
    """

    result = schema.execute(query, variables={"input": {"option": option.pk}})
    assert not result.errors
    with pytest.raises(models.Option.DoesNotExist):
        option.refresh_from_db()
