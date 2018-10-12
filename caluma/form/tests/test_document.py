import pytest

from .. import serializers
from ...form.models import Question
from ...schema import schema
from ...tests import extract_serializer_input_fields


@pytest.mark.parametrize(
    "question__type,answer__value",
    [
        (Question.TYPE_INTEGER, 1),
        (Question.TYPE_FLOAT, 2.1),
        (Question.TYPE_TEXT, "somevalue"),
        (Question.TYPE_CHECKBOX, ["somevalue", "anothervalue"]),
    ],
)
def test_query_all_documents(db, snapshot, form_question, form, document, answer):

    query = """
        query AllDocumentsQuery($search: String) {
          allDocuments(search: $search) {
            edges {
              node {
                answers {
                  edges {
                    node {
                      __typename
                      question {
                        slug
                        label
                      }
                      ... on StringAnswer {
                        string_value: value
                      }
                      ... on IntegerAnswer {
                        integer_value: value
                      }
                      ... on ListAnswer {
                        list_value: value
                      }
                      ... on FloatAnswer {
                        float_value: value
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    search = isinstance(answer.value, list) and " ".join(answer.value) or answer.value
    result = schema.execute(query, variables={"search": search})
    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_document(db, snapshot, document):
    query = """
        mutation SaveDocument($input: SaveDocumentInput!) {
          saveDocument(input: $input) {
            document {
                form {
                    slug
                }
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.DocumentSerializer, document
        )
    }
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("option__slug", ["option-slug"])
@pytest.mark.parametrize(
    "question__type,question__configuration,answer__value,mutation,success",
    [
        (Question.TYPE_INTEGER, {}, 1, "SaveDocumentIntegerAnswer", True),
        (
            Question.TYPE_INTEGER,
            {"min_value": 100},
            1,
            "SaveDocumentIntegerAnswer",
            False,
        ),
        (Question.TYPE_FLOAT, {}, 2.1, "SaveDocumentFloatAnswer", True),
        (
            Question.TYPE_FLOAT,
            {"min_value": 100.0},
            1,
            "SaveDocumentFloatAnswer",
            False,
        ),
        (Question.TYPE_TEXT, {}, "Test", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_TEXT,
            {"max_length": 1},
            "toolong",
            "SaveDocumentStringAnswer",
            False,
        ),
        (
            Question.TYPE_TEXTAREA,
            {"max_length": 1},
            "toolong",
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_CHECKBOX, {}, ["option-slug"], "SaveDocumentListAnswer", True),
        (
            Question.TYPE_CHECKBOX,
            {},
            ["option-slug", "option-invalid-slug"],
            "SaveDocumentStringAnswer",
            False,
        ),
        (Question.TYPE_RADIO, {}, "option-slug", "SaveDocumentStringAnswer", True),
        (
            Question.TYPE_RADIO,
            {},
            "invalid-option-slug",
            "SaveDocumentStringAnswer",
            False,
        ),
    ],
)
def test_save_document_answer(db, snapshot, answer, mutation, question_option, success):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            answer {{
              ... on StringAnswer {{
                stringValue: value
              }}
              ... on IntegerAnswer {{
                integerValue: value
              }}
              ... on ListAnswer {{
                listValue: value
              }}
              ... on FloatAnswer {{
                floatValue: value
              }}
              ... on ListAnswer {{
                listValue: value
              }}
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveAnswerSerializer, answer
        )
    }
    result = schema.execute(query, variables=inp)

    assert not bool(result.errors) == success
    if success:
        snapshot.assert_match(result.data)
