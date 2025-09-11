import warnings

import pytest
from django.utils import translation

from caluma.deprecation import CalumaDeprecationWarning

from ...caluma_core.tests import extract_serializer_input_fields
from ..format_validators import (
    FORMAT_VALIDATION_FAILED,
    BaseFormatValidator,
    base_format_validators,
)
from ..models import Question
from ..serializers import SaveAnswerSerializer

with warnings.catch_warnings():
    # Explicitly ignore the expected deprecation warning as we raise warnings to
    # errors while testing. We explicitly want to test that it still works with
    # the deprecated syntax.
    warnings.filterwarnings("ignore", category=CalumaDeprecationWarning)

    class MyFormatValidator(BaseFormatValidator):
        slug = "test-validator"
        name = {"en": "test name english", "de": "test name deutsch"}
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        error_msg = {"en": "Not valid", "de": "Nicht valid"}


class MyDateValidator(BaseFormatValidator):
    slug = "my-date-validator"
    name = "my date validator"
    error_msg = "%(day)s is not an even day"
    allowed_question_types = [Question.TYPE_DATE]

    @classmethod
    def is_valid(cls, value, document):
        return value.day % 2 == 0

    @classmethod
    def get_error_msg_args(cls, value, document):
        return dict(day=value.day)


def test_fetch_format_validators(snapshot, schema_executor, settings):
    settings.FORMAT_VALIDATOR_CLASSES = [
        "caluma.caluma_form.tests.test_format_validators.MyFormatValidator",
        "caluma.caluma_form.tests.test_format_validators.MyDateValidator",
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
                allowedQuestionTypes
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
    "question__format_validators,answer__value,expected_error",
    [
        (["email"], "some text", "Please enter a valid e-mail address"),
        (["email"], "", None),
        (["email"], "test@example.com", None),
        (["phone-number"], "some text", "Please enter a valid phone number"),
        (["phone-number"], "+411234567890", None),
        (
            ["email", "phone-number"],
            "+411234567890",
            "Please enter a valid e-mail address",
        ),
        (
            ["email", "phone-number"],
            "test@example.com",
            "Please enter a valid phone number",
        ),
    ],
)
def test_base_format_validators(
    db, snapshot, question, answer, expected_error, schema_executor
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

    success = expected_error is None
    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)
    if not success:
        assert result.errors[0].extensions.get("code") == FORMAT_VALIDATION_FAILED
        assert result.errors[0].message == expected_error


@pytest.mark.parametrize(
    "question__type,question__format_validators",
    [(Question.TYPE_DATE, ["my-date-validator"])],
)
@pytest.mark.parametrize(
    "answer__value,success",
    [("2025-09-04", True), ("2025-09-05", False)],
)
def test_custom_format_validators(
    db, question, answer, success, schema_executor, settings
):
    settings.FORMAT_VALIDATOR_CLASSES = [
        "caluma.caluma_form.tests.test_format_validators.MyDateValidator",
    ]

    query = """
        mutation SaveDocumentDateAnswer($input: SaveDocumentDateAnswerInput!) {
          saveDocumentDateAnswer(input: $input) {
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query,
        variable_values={
            "input": extract_serializer_input_fields(SaveAnswerSerializer, answer)
        },
    )
    assert not bool(result.errors) == success
    if not success:
        assert result.errors[0].extensions.get("code") == FORMAT_VALIDATION_FAILED
        assert result.errors[0].message == "5 is not an even day"
