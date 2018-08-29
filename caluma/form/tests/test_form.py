import pytest
from graphql_relay import to_global_id

from .. import models
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields
from ..serializers import FormSerializer


def test_query_all_forms(db, snapshot, form):
    query = """
        query AllFormsQuery($name: String!) {
          allForms(name: $name) {
            edges {
              node {
                id
                slug
                name
                description
                meta
                questions {
                  edges {
                    node {
                      id
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

    result = schema.execute(query, variables={"name": form.name})

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_form(db, snapshot, form):
    query = """
        mutation SaveForm($input: SaveFormInput!) {
          saveForm(input: $input) {
            form {
              id
              slug
              name
              meta
            }
            clientMutationId
          }
        }
    """

    inp = {"input": extract_serializer_input_fields(FormSerializer, form)}
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_archive_form(db, form):
    query = """
        mutation ArchiveForm($input: ArchiveFormInput!) {
          archiveForm(input: $input) {
            form {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(form)}
    )

    assert not result.errors
    assert result.data["archiveForm"]["form"]["isArchived"]

    form.refresh_from_db()
    assert form.is_archived


def test_publish_form(db, form):
    query = """
        mutation PublishForm($input: PublishFormInput!) {
          publishForm(input: $input) {
            form {
              isPublished
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(form)}
    )

    assert not result.errors
    assert result.data["publishForm"]["form"]["isPublished"]

    form.refresh_from_db()
    assert form.is_published


@pytest.mark.parametrize("form__is_published", (True, False))
def test_add_form_question(db, form, question, snapshot):
    query = """
        mutation AddFormQuestion($input: AddFormQuestionInput!) {
          addFormQuestion(input: $input) {
            form {
              questions {
                edges {
                  node {
                    slug
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={
            "input": {
                "formId": to_global_id(type(form).__name__, form.pk),
                "questionId": to_global_id(type(question).__name__, question.pk),
            }
        },
    )

    snapshot.assert_execution_result(result)


@pytest.mark.parametrize("form__is_published", (True, False))
def test_remove_form_question(db, form, formquestion, question, snapshot):
    query = """
        mutation RemoveFormQuestion($input: RemoveFormQuestionInput!) {
          removeFormQuestion(input: $input) {
            form {
              questions {
                edges {
                  node {
                    slug
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={
            "input": {
                "formId": to_global_id(type(form).__name__, form.pk),
                "questionId": to_global_id(type(question).__name__, question.pk),
            }
        },
    )

    snapshot.assert_execution_result(result)


def test_reorder_form_questions(db, form, form_question_factory):
    form_question_factory.create_batch(2, form=form)

    query = """
        mutation ReorderFormQuestions($input: ReorderFormQuestionsInput!) {
          reorderFormQuestions(input: $input) {
            form {
              questions {
                edges {
                  node {
                    slug
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    question_ids = (
        form.questions.order_by("slug").reverse().values_list("slug", flat=True)
    )
    result = schema.execute(
        query,
        variables={
            "input": {
                "formId": to_global_id(type(form).__name__, form.pk),
                "questionIds": [
                    to_global_id(type(models.Question).__name__, question_id)
                    for question_id in question_ids
                ],
            }
        },
    )

    assert not result.errors
    result_questions = [
        question["node"]["slug"]
        for question in result.data["reorderFormQuestions"]["form"]["questions"][
            "edges"
        ]
    ]

    assert result_questions == list(question_ids)


def test_reorder_form_questions_invalid_question(db, form):

    query = """
        mutation ReorderFormQuestions($input: ReorderFormQuestionsInput!) {
          reorderFormQuestions(input: $input) {
            form {
              questions {
                edges {
                  node {
                    slug
                  }
                }
              }
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query,
        variables={
            "input": {
                "formId": to_global_id(type(form).__name__, form.pk),
                "questionIds": [
                    to_global_id(type(models.Question).__name__, "invalidquestion")
                ],
            }
        },
    )

    assert result.errors
