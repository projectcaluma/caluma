import pytest

from .. import serializers
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields


def test_query_all_questions(db, snapshot, question, form, form_question_factory):
    form_question_factory.create(form=form)

    query = """
        query AllQuestionsQuery($search: String, $forms: [ID]) {
          allQuestions(isArchived: false, search: $search, excludeForms: $forms) {
            edges {
              node {
                id
                slug
                label
                type
                configuration
                meta
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
            serializers.SaveQuestionSerializer, question
        )
    }
    result = schema.execute(query, variables=inp)
    snapshot.assert_execution_result(result)


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
