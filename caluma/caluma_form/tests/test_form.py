import pytest
from django.utils import translation
from graphql_relay import to_global_id

from ...caluma_core.tests import extract_serializer_input_fields
from .. import models
from ..serializers import SaveFormSerializer


@pytest.mark.parametrize(
    "form__description,form__name,question__type",
    [("First result", "1st", models.Question.TYPE_FLOAT)],
)
def test_query_all_forms(
    db,
    snapshot,
    form,
    form_factory,
    form_question,
    form_question_factory,
    question,
    schema_executor,
):
    form_factory(name="3rd", description="Second result")
    form_factory(name="2nd", description="Second result")
    form_question_factory(form=form)

    query = """
        query AllFormsQuery($name: String, $question: String, $orderBy: [FormOrdering]) {
          allForms(name: $name, orderBy: $orderBy) {
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

    result = schema_executor(
        query,
        variable_values={
            "question": question.label,
            "orderBy": ["NAME_ASC", "CREATED_AT_ASC"],
        },
    )

    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("language_code", ("en", "de"))
@pytest.mark.parametrize("form__description", ("some description text", ""))
def test_save_form(db, snapshot, form, settings, schema_executor, language_code):
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

    inp = {"input": extract_serializer_input_fields(SaveFormSerializer, form)}
    with translation.override(language_code):
        result = schema_executor(query, variable_values=inp)

    assert not result.errors
    snapshot.assert_match(result.data)


def test_save_form_created_as_admin_user(db, form, admin_schema_executor, admin_user):
    query = """
        mutation SaveForm($input: SaveFormInput!) {
          saveForm(input: $input) {
            form {
              createdByUser
            }
          }
        }
    """

    inp = {"input": extract_serializer_input_fields(SaveFormSerializer, form)}
    form.delete()  # test creation of form
    result = admin_schema_executor(query, variable_values=inp)

    assert not result.errors
    assert result.data["saveForm"]["form"]["createdByUser"] == admin_user.username


@pytest.mark.parametrize("form__meta", [{"meta": "set"}])
def test_copy_form(db, form, form_question_factory, schema_executor):
    form_question_factory.create_batch(5, form=form)
    query = """
        mutation CopyForm($input: CopyFormInput!) {
          copyForm(input: $input) {
            form {
              slug
            }
            clientMutationId
          }
        }
    """

    inp = {"input": {"source": form.pk, "slug": "new-form", "name": "Test Form"}}
    result = schema_executor(query, variable_values=inp)

    assert not result.errors

    form_slug = result.data["copyForm"]["form"]["slug"]
    assert form_slug == "new-form"
    new_form = models.Form.objects.get(pk=form_slug)
    assert new_form.name == "Test Form"
    assert new_form.meta == form.meta
    assert new_form.source == form
    assert list(
        models.FormQuestion.objects.filter(form=new_form).values("question")
    ) == list(models.FormQuestion.objects.filter(form=form).values("question"))


def test_add_form_question(db, form, question, form_question_factory, schema_executor):
    form_questions = form_question_factory.create_batch(5, form=form)

    # initialize sorting keys
    for idx, form_question in enumerate(form_questions):
        form_question.sort = idx + 1
        form_question.save()

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

    result = schema_executor(
        query,
        variable_values={
            "input": {
                "form": to_global_id(type(form).__name__, form.pk),
                "question": to_global_id(type(question).__name__, question.pk),
            }
        },
    )

    assert not result.errors
    questions = result.data["addFormQuestion"]["form"]["questions"]["edges"]
    assert len(questions) == 6
    assert questions[-1]["node"]["slug"] == question.slug


def test_remove_form_question(
    db, form, form_question, question, snapshot, schema_executor
):
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

    result = schema_executor(
        query,
        variable_values={
            "input": {
                "form": to_global_id(type(form).__name__, form.pk),
                "question": to_global_id(type(question).__name__, question.pk),
            }
        },
    )

    assert not result.errors
    snapshot.assert_match(result.data)


def test_reorder_form_questions(db, form, form_question_factory, schema_executor):
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
    result = schema_executor(
        query,
        variable_values={
            "input": {
                "form": to_global_id(type(form).__name__, form.pk),
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
        for question in result.data["reorderFormQuestions"]["form"]["questions"][
            "edges"
        ]
    ]

    assert result_questions == list(question_ids)


def test_reorder_form_questions_invalid_question(
    db, form, question_factory, schema_executor
):

    invalid_question = question_factory()

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

    result = schema_executor(
        query,
        variable_values={
            "input": {
                "form": to_global_id(type(form).__name__, form.pk),
                "questions": [
                    to_global_id(type(models.Question).__name__, invalid_question.slug)
                ],
            }
        },
    )

    assert result.errors


def test_reorder_form_questions_duplicated_question(
    db, form, question, form_question, schema_executor
):

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

    result = schema_executor(
        query,
        variable_values={
            "input": {
                "form": to_global_id(type(form).__name__, form.pk),
                "questions": [question.slug, question.slug],
            }
        },
    )
    assert result.errors
