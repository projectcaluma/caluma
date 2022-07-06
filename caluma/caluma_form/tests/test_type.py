import pytest
from graphql_relay import to_global_id

from .. import models


@pytest.mark.parametrize(
    "question__type,expected_typename,success",
    [
        (models.Question.TYPE_FILE, "FileAnswer", True),
        (models.Question.TYPE_TEXT, "StringAnswer", True),
        (models.Question.TYPE_TEXTAREA, "StringAnswer", True),
        (models.Question.TYPE_FLOAT, "FloatAnswer", True),
        (models.Question.TYPE_CHOICE, "StringAnswer", True),
        (models.Question.TYPE_INTEGER, "IntegerAnswer", True),
        (models.Question.TYPE_MULTIPLE_CHOICE, "ListAnswer", True),
        (models.Question.TYPE_DYNAMIC_CHOICE, "StringAnswer", True),
        (models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, "ListAnswer", True),
        (models.Question.TYPE_DATE, "DateAnswer", True),
        (models.Question.TYPE_TABLE, "TableAnswer", True),
        (models.Question.TYPE_STATIC, "StringAnswer", False),
    ],
)
def test_answer_types(
    db, question, expected_typename, success, answer_factory, schema_executor
):
    answer = answer_factory(question=question)
    global_id = to_global_id(expected_typename, answer.pk)

    query = """
        query Answer($id: ID!) {
            node(id: $id) {
              id
              __typename
            }
        }
    """

    result = schema_executor(query, variable_values={"id": global_id})
    assert not result.errors == success
    if success:
        assert result.data["node"]["__typename"] == expected_typename


@pytest.mark.parametrize(
    "question__type,expected_typename",
    [
        (models.Question.TYPE_TEXT, "TextQuestion"),
        (models.Question.TYPE_FLOAT, "FloatQuestion"),
        (models.Question.TYPE_CHOICE, "ChoiceQuestion"),
        (models.Question.TYPE_INTEGER, "IntegerQuestion"),
        (models.Question.TYPE_MULTIPLE_CHOICE, "MultipleChoiceQuestion"),
        (models.Question.TYPE_DYNAMIC_CHOICE, "DynamicChoiceQuestion"),
        (models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, "DynamicMultipleChoiceQuestion"),
        (models.Question.TYPE_TEXTAREA, "TextareaQuestion"),
        (models.Question.TYPE_DATE, "DateQuestion"),
        (models.Question.TYPE_TABLE, "TableQuestion"),
        (models.Question.TYPE_FORM, "FormQuestion"),
        (models.Question.TYPE_FILE, "FileQuestion"),
        (models.Question.TYPE_STATIC, "StaticQuestion"),
    ],
)
def test_question_types(
    db, question, expected_typename, answer_factory, schema_executor
):
    global_id = to_global_id(expected_typename, question.pk)

    query = """
        query Question($id: ID!) {
            node(id: $id) {
              id
              __typename
            }
        }
    """

    result = schema_executor(query, variable_values={"id": global_id})
    assert not result.errors
    assert result.data["node"]["__typename"] == expected_typename
