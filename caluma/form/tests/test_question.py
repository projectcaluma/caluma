import pytest
from graphql.error import format_error

from .. import serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


@pytest.mark.parametrize("question__is_required", ("true", "true|invalid"))
def test_save_question(db, snapshot, question):
    query = """
        mutation SaveQuestion($input: SaveQuestionInput!) {
          saveQuestion(input: $input) {
            question {
                id
                slug
                label
                type
                configuration
                meta
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.QuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)
    snapshot.assert_match(
        {"data": result.data, "errors": [format_error(e) for e in result.errors or []]}
    )


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
