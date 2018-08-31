import pytest

from ...form.models import Question
from ...schema import schema


@pytest.mark.parametrize(
    "question__type,answer__value",
    [
        (Question.TYPE_INTEGER, 1),
        (Question.TYPE_FLOAT, 2.1),
        (Question.TYPE_TEXT, "Test"),
        (Question.TYPE_CHECKBOX, ["123", "1"]),
    ],
)
def test_query_all_documents(db, snapshot, formquestion, form, document, answer):

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
