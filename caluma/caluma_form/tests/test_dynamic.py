import json

import pytest

from caluma.caluma_form.models import Question


@pytest.mark.parametrize("question__data_source", ["MyDataSourceWithContext"])
@pytest.mark.parametrize(
    "question__type",
    [Question.TYPE_DYNAMIC_CHOICE, Question.TYPE_DYNAMIC_MULTIPLE_CHOICE],
)
@pytest.mark.parametrize("context", [{"foo": "bar"}, None])
def test_dynamic_choice_options_context(
    db, snapshot, question, schema_executor, settings, context
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSourceWithContext"
    ]

    query = """
        query($question: String!, $context: JSONString) {
            allQuestions(filter: { slugs: [$question] }) {
                edges {
                    node {
                        id
                        ...on DynamicChoiceQuestion {
                            options(context: $context) {
                                edges {
                                    node {
                                        slug
                                        label
                                    }
                                }
                            }
                        }
                        ...on DynamicMultipleChoiceQuestion {
                            options(context: $context) {
                                edges {
                                    node {
                                        slug
                                        label
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    variables = {"question": question.pk}

    if context:
        variables["context"] = json.dumps(context)

    result = schema_executor(query, variable_values=variables)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__data_source", ["MyDataSourceWithContext"])
@pytest.mark.parametrize(
    "question__type,value,context,success",
    [
        (Question.TYPE_DYNAMIC_CHOICE, "option-with-context", {"foo": "bar"}, True),
        (Question.TYPE_DYNAMIC_CHOICE, "option-with-context", None, False),
        (Question.TYPE_DYNAMIC_CHOICE, "option-without-context", None, True),
        (Question.TYPE_DYNAMIC_CHOICE, "option-without-context", {"foo": "bar"}, False),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["option-with-context"],
            {"foo": "bar"},
            True,
        ),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, ["option-with-context"], None, False),
        (Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, ["option-without-context"], None, True),
        (
            Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            ["option-without-context"],
            {"foo": "bar"},
            False,
        ),
    ],
)
def test_save_dynamic_choice_options_context(
    db, snapshot, question, document, schema_executor, settings, value, context, success
):
    settings.DATA_SOURCE_CLASSES = [
        "caluma.caluma_data_source.tests.data_sources.MyDataSourceWithContext"
    ]

    if question.type == Question.TYPE_DYNAMIC_CHOICE:
        query = """
            mutation($input: SaveDocumentStringAnswerInput!) {
                saveDocumentStringAnswer(input: $input) {
                    answer {
                        ...on StringAnswer {
                            selectedOption {
                                slug
                                label
                            }
                        }
                    }
                }
            }
        """
    elif question.type == Question.TYPE_DYNAMIC_MULTIPLE_CHOICE:
        query = """
            mutation($input: SaveDocumentListAnswerInput!) {
                saveDocumentListAnswer(input: $input) {
                    answer {
                        ...on ListAnswer {
                            selectedOptions {
                                edges {
                                    node {
                                        slug
                                        label
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """

    variables = {
        "input": {
            "question": question.pk,
            "document": str(document.pk),
            "value": value,
            "dataSourceContext": json.dumps(context),
        }
    }

    result = schema_executor(query, variable_values=variables)

    assert bool(result.errors) != success
    snapshot.assert_match(result.data)
