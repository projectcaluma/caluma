import pytest

from .. import models


@pytest.mark.parametrize(
    "question__type,answer__value", [(models.Question.TYPE_INTEGER, 23)]
)
def test_remove_answer(db, snapshot, question, answer, schema_executor):
    query = """
        mutation RemoveAnswer($input: RemoveAnswerInput!) {
          removeAnswer(input: $input) {
            answer {
              id
              meta
              __typename
            }
            clientMutationId
          }
        }
    """

    result = schema_executor(
        query, variable_values={"input": {"answer": str(answer.pk)}}
    )

    assert not result.errors
    with pytest.raises(models.Answer.DoesNotExist):
        answer.refresh_from_db()

    snapshot.assert_match(result.data)
