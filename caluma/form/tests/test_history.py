import pytest
from simple_history.models import HistoricalRecords

from .. import models


@pytest.mark.parametrize("question__type", [models.Question.TYPE_TEXT])
def test_history(db, question, document, schema_executor, admin_schema_executor):
    query = """
        mutation MyStringAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer (input: $input) {
            answer {
              id
            }
          }
        }
    """

    HistoricalRecords.thread.request = admin_schema_executor.keywords["context"]

    result = admin_schema_executor(
        query,
        variables={
            "input": {
                "question": str(question.pk),
                "value": "dolor",
                "document": str(document.pk),
            }
        },
    )
    assert not result.errors
    assert (
        models.Answer.history.get(value="dolor").history_user
        == admin_schema_executor.keywords["context"].user.username
    )

    query = """
            mutation MyStringAnswer($input: SaveDocumentStringAnswerInput!) {
              saveDocumentStringAnswer (input: $input) {
                answer {
                  id
                }
              }
            }
        """

    HistoricalRecords.thread.request = schema_executor.keywords["context"]

    result = schema_executor(
        query,
        variables={
            "input": {
                "question": str(question.pk),
                "value": "sit",
                "document": str(document.pk),
            }
        },
    )
    assert not result.errors
    assert models.Answer.history.count() == 2
    history = models.Answer.history.all()
    assert (
        history[1].history_user
        == admin_schema_executor.keywords["context"].user.username
    )
    assert history[1].value == "dolor"

    assert history[0].history_user is None
    assert history[0].value == "sit"
