import pytest
from graphql_relay import to_global_id

from .. import models
from ...schema import schema
from ...tests import extract_global_id_input_fields, extract_serializer_input_fields
from ..serializers import SaveFormSpecificationSerializer


def test_query_all_form_specifications(
    db, snapshot, form_specification, form_specification_question, question
):
    query = """
        query AllFormSpecificationsQuery($name: String!, $question: String!) {
          allFormSpecifications(name: $name) {
            edges {
              node {
                id
                slug
                name
                description
                meta
                questions(search: $question) {
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

    result = schema.execute(
        query, variables={"name": form_specification.name, "question": question.label}
    )

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize(
    "form_specification__description", ("some description text", "")
)
def test_save_form_specification(db, snapshot, form_specification):
    query = """
        mutation SaveFormSpecification($input: SaveFormSpecificationInput!) {
          saveFormSpecification(input: $input) {
            formSpecification {
              id
              slug
              name
              meta
            }
            clientMutationId
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            SaveFormSpecificationSerializer, form_specification
        )
    }
    form_specification.delete()  # test creation of form specification
    result = schema.execute(query, variables=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_archive_form_specification(db, form_specification):
    query = """
        mutation ArchiveFormSpecification($input: ArchiveFormSpecificationInput!) {
          archiveFormSpecification(input: $input) {
            formSpecification {
              isArchived
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(form_specification)}
    )

    assert not result.errors
    assert result.data["archiveFormSpecification"]["formSpecification"]["isArchived"]

    form_specification.refresh_from_db()
    assert form_specification.is_archived


def test_publish_form_specification(db, form_specification):
    query = """
        mutation PublishFormSpecification($input: PublishFormSpecificationInput!) {
          publishFormSpecification(input: $input) {
            formSpecification {
              isPublished
            }
            clientMutationId
          }
        }
    """

    result = schema.execute(
        query, variables={"input": extract_global_id_input_fields(form_specification)}
    )

    assert not result.errors
    assert result.data["publishFormSpecification"]["formSpecification"]["isPublished"]

    form_specification.refresh_from_db()
    assert form_specification.is_published


def test_add_form_specification_question(db, form_specification, question, snapshot):
    query = """
        mutation AddFormSpecificationQuestion($input: AddFormSpecificationQuestionInput!) {
          addFormSpecificationQuestion(input: $input) {
            formSpecification {
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
                "formSpecification": to_global_id(
                    type(form_specification).__name__, form_specification.pk
                ),
                "question": to_global_id(type(question).__name__, question.pk),
            }
        },
    )

    snapshot.assert_execution_result(result)


def test_remove_form_specification_question(
    db, form_specification, form_specification_question, question, snapshot
):
    query = """
        mutation RemoveFormSpecificationQuestion($input: RemoveFormSpecificationQuestionInput!) {
          removeFormSpecificationQuestion(input: $input) {
            formSpecification {
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
                "formSpecification": to_global_id(
                    type(form_specification).__name__, form_specification.pk
                ),
                "question": to_global_id(type(question).__name__, question.pk),
            }
        },
    )

    assert not result.errors
    snapshot.assert_match(result.data)


def test_reorder_form_specification_questions(
    db, form_specification, form_specification_question_factory
):
    form_specification_question_factory.create_batch(
        2, form_specification=form_specification
    )

    query = """
        mutation ReorderFormSpecificationQuestions($input: ReorderFormSpecificationQuestionsInput!) {
          reorderFormSpecificationQuestions(input: $input) {
            formSpecification {
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
        form_specification.questions.order_by("slug")
        .reverse()
        .values_list("slug", flat=True)
    )
    result = schema.execute(
        query,
        variables={
            "input": {
                "formSpecification": to_global_id(
                    type(form_specification).__name__, form_specification.pk
                ),
                "questions": [
                    to_global_id(type(models.Question).__name__, question_id)
                    for question_id in question_ids
                ],
            }
        },
    )

    assert not result.errors
    result_questions = [
        question["node"]["slug"]
        for question in result.data["reorderFormSpecificationQuestions"][
            "formSpecification"
        ]["questions"]["edges"]
    ]

    assert result_questions == list(question_ids)


def test_reorder_form_specification_questions_invalid_question(
    db, form_specification, question_factory
):

    invalid_question = question_factory()

    query = """
        mutation ReorderFormSpecificationQuestions($input: ReorderFormSpecificationQuestionsInput!) {
          reorderFormSpecificationQuestions(input: $input) {
            formSpecification {
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
                "formSpecification": to_global_id(
                    type(form_specification).__name__, form_specification.pk
                ),
                "questions": [
                    to_global_id(type(models.Question).__name__, invalid_question.slug)
                ],
            }
        },
    )

    assert result.errors
