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
        (Question.TYPE_TEXT, "Test"),
        (Question.TYPE_CHECKBOX, ["123", "1"]),
    ],
)
def test_query_all_documents(db, snapshot, form_question, form, document, answer):

    query = """
        query AllDocumentsQuery {
          allDocuments {
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

    result = schema.execute(query)
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


@pytest.mark.parametrize(
    "question__type,answer__value,mutation",
    [
        (Question.TYPE_INTEGER, 1, "SaveDocumentIntegerAnswer"),
        (Question.TYPE_FLOAT, 2.1, "SaveDocumentFloatAnswer"),
        (Question.TYPE_TEXT, "Test", "SaveDocumentStringAnswer"),
        (Question.TYPE_CHECKBOX, ["123", "1"], "SaveDocumentListAnswer"),
    ],
)
def test_save_document_answer(db, snapshot, answer, mutation):
    mutation_func = mutation[0].lower() + mutation[1:]
    query = f"""
        mutation {mutation}($input: {mutation}Input!) {{
          {mutation_func}(input: $input) {{
            answer {{
              ... on StringAnswer {{
                string_value: value
              }}
              ... on IntegerAnswer {{
                integer_value: value
              }}
              ... on ListAnswer {{
                list_value: value
              }}
              ... on FloatAnswer {{
                float_value: value
              }}
            }}
            clientMutationId
          }}
        }}
    """

    inp = {
        "input": extract_serializer_input_fields(serializers.AnswerSerializer, answer)
    }
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)
