import pytest

from .. import models, serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


@pytest.mark.parametrize(
    "question__type,question__configuration",
    [
        (models.Question.TYPE_INTEGER, {"max_value": 10, "min_value": 0}),
        (models.Question.TYPE_FLOAT, {"max_value": 1.0, "min_value": 0.0}),
        (models.Question.TYPE_FLOAT, {}),
        (models.Question.TYPE_TEXT, {"max_length": 10}),
        (models.Question.TYPE_TEXTAREA, {"max_length": 10}),
        (models.Question.TYPE_RADIO, {}),
        (models.Question.TYPE_CHECKBOX, {}),
    ],
)
def test_query_all_questions(
    db, snapshot, question, form, form_question_factory, question_option
):
    form_question_factory.create(form=form)

    query = """
        query AllQuestionsQuery($search: String, $forms: [ID]) {
          allQuestions(isArchived: false, search: $search, excludeForms: $forms) {
            edges {
              node {
                id
                __typename
                slug
                label
                meta
                ... on TextQuestion {
                  maxLength
                }
                ... on TextareaQuestion {
                  maxLength
                }
                ... on FloatQuestion {
                  floatMinValue: minValue
                  floatMaxValue: maxValue
                }
                ... on IntegerQuestion {
                  integerMinValue: minValue
                  integerMaxValue: maxValue
                }
                ... on CheckboxQuestion {
                  options {
                    edges {
                      node {
                        slug
                      }
                    }
                  }
                }
                ... on RadioQuestion {
                  options {
                    edges {
                      node {
                        slug
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    result = schema.execute(
        query,
        variables={
            "search": question.label,
            "forms": [extract_global_id_input_fields(form)["id"]],
        },
    )

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "mutation",
    [
        "SaveTextQuestion",
        "SaveTextareaQuestion",
        "SaveIntegerQuestion",
        "SaveFloatQuestion",
    ],
)
@pytest.mark.parametrize("question__is_required", ("true", "true|invalid"))
def test_save_question(db, snapshot, question, mutation):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            question {{
              id
              slug
              label
              meta
              __typename
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveQuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)

    snapshot.assert_execution_result(result)


@pytest.mark.parametrize(
    "question__type,question__configuration",
    [(models.Question.TYPE_TEXT, {"max_length": 10})],
)
def test_save_text_question(db, snapshot, question):
    query = """
        mutation SaveTextQuestion($input: SaveTextQuestionInput!) {
          saveTextQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on TextQuestion {
                maxLength
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveTextQuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)
    assert not result.errors
    assert result.data["saveTextQuestion"]["question"]["maxLength"] == 10


@pytest.mark.parametrize(
    "question__type,question__configuration",
    [(models.Question.TYPE_TEXTAREA, {"max_length": 10})],
)
def test_save_textarea_question(db, snapshot, question):
    query = """
        mutation SaveTextareaQuestion($input: SaveTextareaQuestionInput!) {
          saveTextareaQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on TextareaQuestion {
                maxLength
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveTextareaQuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)
    assert not result.errors
    assert result.data["saveTextareaQuestion"]["question"]["maxLength"] == 10


@pytest.mark.parametrize(
    "question__type,question__configuration",
    [
        (models.Question.TYPE_FLOAT, {"max_value": 10.0, "min_value": 0.0}),
        (models.Question.TYPE_FLOAT, {"max_value": 1.0, "min_value": 10.0}),
    ],
)
def test_save_float_question(db, snapshot, question):
    query = """
        mutation SaveFloatQuestion($input: SaveFloatQuestionInput!) {
          saveFloatQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on FloatQuestion {
                minValue
                maxValue
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveFloatQuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)
    snapshot.assert_execution_result(result)


@pytest.mark.parametrize(
    "question__type,question__configuration",
    [
        (models.Question.TYPE_INTEGER, {"max_value": 10, "min_value": 0}),
        (models.Question.TYPE_INTEGER, {"max_value": 1, "min_value": 10}),
    ],
)
def test_save_integer_question(db, snapshot, question):
    query = """
        mutation SaveIntegerQuestion($input: SaveIntegerQuestionInput!) {
          saveIntegerQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on FloatQuestion {
                minValue
                maxValue
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveIntegerQuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)
    snapshot.assert_execution_result(result)


@pytest.mark.parametrize("question__type", [models.Question.TYPE_CHECKBOX])
def test_save_checkbox_question(db, snapshot, question, question_option_factory):
    question_option_factory.create_batch(2, question=question)

    option_ids = (
        question.options.order_by("slug").reverse().values_list("slug", flat=True)
    )

    query = """
        mutation SaveCheckboxQuestion($input: SaveCheckboxQuestionInput!) {
          saveCheckboxQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on CheckboxQuestion {
                options {
                  edges {
                    node {
                      slug
                      label
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveCheckboxQuestionSerializer, question
        )
    }
    inp["input"]["options"] = option_ids
    result = schema.execute(query, variables=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("question__type", [models.Question.TYPE_RADIO])
def test_save_radio_question(db, snapshot, question, question_option):
    query = """
        mutation SaveRadioQuestion($input: SaveRadioQuestionInput!) {
          saveRadioQuestion(input: $input) {
            question {
              id
              slug
              label
              meta
              __typename
              ... on RadioQuestion {
                options {
                  edges {
                    node {
                      slug
                      label
                    }
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveRadioQuestionSerializer, question
        )
    }
    question.delete()  # test creation
    result = schema.execute(query, variables=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


def test_archive_question(db, question):
    query = """
        mutation ArchiveQuestion($input: ArchiveQuestionInput!) {
          archiveQuestion(input: $input) {
            question {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(question)}
    )

    assert not result.errors
    assert result.data["archiveQuestion"]["question"]["isArchived"]

    question.refresh_from_db()
    assert question.is_archived
