import pytest

from ...caluma_core.tests import extract_serializer_input_fields
from .. import models, serializers


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

    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


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
    result = schema_executor(query, variable_values=inp)

    assert not result.errors

    option_slug = result.data["copyOption"]["option"]["slug"]
    assert option_slug == "new-option"
    new_option = models.Option.objects.get(pk=option_slug)
    assert new_option.label == "Test Option"
    assert new_option.meta == option.meta
    assert new_option.source == option


def test_dynamic_option(db, schema_executor, dynamic_option_factory):
    query = """
        query dynamicOptions ($filter:[DynamicOptionFilterSetType]) {
          allUsedDynamicOptions(filter: $filter){
            edges{
              node{
                slug
                label
              }
            }
          }
        }
    """

    dynamic_option = dynamic_option_factory()
    inp = {"filter": [{"document": dynamic_option.id}]}
    result = schema_executor(query, variable_values=inp)

    assert not result.errors
    assert dynamic_option.slug == "service-bank-arm"
    assert dynamic_option.label["en"] == "Calvin Graham"
