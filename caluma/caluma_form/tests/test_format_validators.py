import pytest
from django.utils import translation

from ...caluma_core.tests import extract_serializer_input_fields
from ..format_validators import BaseFormatValidator, base_format_validators
from ..models import Question
from ..serializers import SaveAnswerSerializer


class MyFormatValidator(BaseFormatValidator):
    slug = "test-validator"
    name = {"en": "test name english", "de": "test name deutsch"}
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    error_msg = {"en": "Not valid", "de": "Nicht valid"}


def test_fetch_format_validators(snapshot, schema_executor, settings):
    settings.FORMAT_VALIDATOR_CLASSES = [
        "caluma.caluma_form.tests.test_format_validators.MyFormatValidator"
    ]
    query = """
        query formatValidators {
          allFormatValidators {
            pageInfo {
              startCursor
              endCursor
            }
            totalCount
            edges {
              node {
                slug
                name
                regex
                errorMsg
              }
            }
          }
        }
    """

    result = schema_executor(query)
    assert not result.errors
    snapshot.assert_match(result.data)

    with translation.override("de"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)

    with translation.override("fr"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)

    with translation.override("nolang"):
        result = schema_executor(query)
        assert not result.errors
        snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__type", [Question.TYPE_TEXT, Question.TYPE_TEXTAREA])
@pytest.mark.parametrize(
    "question__format_validators,answer__value,success",
    [
        (["email"], "some text", False),
        (["email"], "test@example.com", True),
        (["phone-number"], "some text", False),
        (["phone-number"], "+411234567890", True),
        (["email", "phone-number"], "+411234567890", False),
        (["email", "phone-number"], "test@example.com", False),
    ],
)
def test_base_format_validators(
    db, snapshot, question, answer, success, schema_executor
):
    query = """
        mutation SaveDocumentStringAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer(input: $input) {
            answer {
              ... on StringAnswer {
                stringValue: value
              }
            }
            clientMutationId
          }
        }
    """

    inp = {"input": extract_serializer_input_fields(SaveAnswerSerializer, answer)}

    result = schema_executor(query, variable_values=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)
    if not success:
        error_msgs = [fv.error_msg["en"] for fv in base_format_validators]
        assert (
            str(result.errors[0].original_error.detail["non_field_errors"][0])
            in error_msgs
        )
