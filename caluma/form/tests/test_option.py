import pytest

from .. import models, serializers
from ...core.tests import extract_serializer_input_fields


def test_save_option(db, option, snapshot, schema_executor):
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

    result = schema_executor(query, variables=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


def test_remove_option(db, option, schema_executor):
    query = """
        mutation RemoveOption($input: RemoveOptionInput!) {
          removeOption(input: $input) {
            clientMutationId
          }
        }
    """

    result = schema_executor(query, variables={"input": {"option": option.pk}})
    assert not result.errors
    with pytest.raises(models.Option.DoesNotExist):
        option.refresh_from_db()


@pytest.mark.parametrize("option__meta", [{"meta": "set"}])
def test_copy_option(db, option, schema_executor):
    query = """
        mutation CopyOption($input: CopyOptionInput!) {
          copyOption(input: $input) {
            option {
              slug
            }
          }
        }
    """

    inp = {"input": {"source": option.pk, "slug": "new-option", "label": "Test Option"}}
    result = schema_executor(query, variables=inp)

    assert not result.errors

    option_slug = result.data["copyOption"]["option"]["slug"]
    assert option_slug == "new-option"
    new_option = models.Option.objects.get(pk=option_slug)
    assert new_option.label == "Test Option"
    assert new_option.meta == option.meta
    assert new_option.source == option
