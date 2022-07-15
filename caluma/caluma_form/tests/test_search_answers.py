import pytest

from ...caluma_core.relay import extract_global_id
from .. import models


def test_search(
    schema_executor,
    db,
    form_factory,
    form_question_factory,
    document_factory,
    answer_factory,
):
    form_a, form_b = form_factory.create_batch(2)
    doc_a = document_factory.create(form=form_a)
    doc_b = document_factory.create(form=form_b)

    question_a = form_question_factory(
        question__type=models.Question.TYPE_TEXT, form=form_a
    ).question
    question_b = form_question_factory(
        question__type=models.Question.TYPE_TEXT, form=form_a
    ).question
    form_question_factory(question=question_a, form=form_b)
    form_question_factory(question=question_b, form=form_b)

    doc_a.answers.create(question=question_a, value="hello world")
    doc_a.answers.create(question=question_b, value="whatsup planet")

    doc_b.answers.create(question=question_a, value="world planet")
    doc_b.answers.create(question=question_b, value="seeya world")

    query = """
        query ($search: [SearchAnswersFilterType!]) {
          allDocuments(filter: [{searchAnswers: $search}]) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    def _search(q_slugs, f_slugs, word, expect_count):
        variables = {
            "search": [{"questions": q_slugs, "forms": f_slugs, "value": word}]
        }
        result = schema_executor(query, variable_values=variables)

        assert not result.errors
        edges = result.data["allDocuments"]["edges"]
        assert len(edges) == expect_count
        return edges

    # search for "hello world". this should return doc a
    edges = _search([question_a.slug], [], "hello world", 1)
    assert extract_global_id(edges[0]["node"]["id"]) == str(doc_a.id)

    # search for "planet" across both questions. this should return both doc a
    # and b
    edges = _search([question_b.slug, question_a.slug], [], "planet", 2)
    assert set([str(doc_a.id), str(doc_b.id)]) == set(
        extract_global_id(e["node"]["id"]) for e in edges
    )

    # search for "world" in form a, it should return doc a
    edges = _search([], [form_a.slug], "world", 1)
    assert extract_global_id(edges[0]["node"]["id"]) == str(doc_a.id)

    # search for "world" in question b and form b. this should return both doc b
    edges = _search([question_a.slug], [form_b.slug], "world", 1)
    assert extract_global_id(edges[0]["node"]["id"]) == str(doc_b.id)


@pytest.mark.parametrize(
    "question_type, search_text",
    [
        (models.Question.TYPE_CHOICE, "hello world"),
        (models.Question.TYPE_DYNAMIC_CHOICE, "hello world"),
        (models.Question.TYPE_MULTIPLE_CHOICE, "hello world"),
        (models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, "hello world"),
        (models.Question.TYPE_CHOICE, "unrelated"),
    ],
)
def test_search_choice(
    schema_executor,
    db,
    form_factory,
    form_question_factory,
    question_factory,
    document_factory,
    answer_factory,
    form,
    question_option_factory,
    question_type,
    search_text,
):
    dynamic = "dynamic" in question_type

    option_factory = (
        models.DynamicOption.objects.create if dynamic else models.Option.objects.create
    )

    doc_a, doc_b = document_factory.create_batch(2, form=form)

    question_a = question_factory(type=question_type)
    if not dynamic:
        opt_a = option_factory(slug="nonmatching-slug", label="hello world")
        opt_b = option_factory(slug="another-slug", label="irrelevant")
        question_option_factory(question=question_a, option=opt_a)
        question_option_factory(question=question_a, option=opt_b)
    question_b = question_factory(type=models.Question.TYPE_TEXT)

    doc_a.answers.create(question=question_a, value="nonmatching-slug")
    doc_a.answers.create(question=question_b, value="whatsup planet")
    if dynamic:
        opt_a = option_factory(
            question=question_a,
            document=doc_a,
            slug="nonmatching-slug",
            label="hello world",
        )
        opt_b = option_factory(
            question=question_a, document=doc_a, slug="another-slug", label="irrelevant"
        )

    doc_b.answers.create(question=question_a, value="another-slug")
    doc_b.answers.create(question=question_b, value="seeya world")

    query = """
        query ($search: [SearchAnswersFilterType!]) {
          allDocuments(filter: [{searchAnswers: $search}]) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    def _search(slugs, word, expect_count):
        variables = {"search": [{"questions": slugs, "value": word}]}
        result = schema_executor(query, variable_values=variables)

        assert not result.errors
        edges = result.data["allDocuments"]["edges"]
        assert len(edges) == expect_count
        return edges

    edges = _search(
        [question_a.slug], search_text, 0 if search_text == "unrelated" else 1
    )
    if search_text != "unrelated":
        assert extract_global_id(edges[0]["node"]["id"]) == str(doc_a.id)


def test_search_multiple(
    schema_executor,
    db,
    question,
    form_factory,
    form_question_factory,
    question_factory,
    document_factory,
    answer_factory,
    form,
):

    doc_a, doc_b, doc_c = document_factory.create_batch(3, form=form)

    question_a = question_factory(type=models.Question.TYPE_TEXT)
    question_b = question_factory(type=models.Question.TYPE_TEXT)

    doc_a.answers.create(question=question_a, value="hello planet")
    doc_a.answers.create(question=question_b, value="whatsup planet")

    doc_b.answers.create(question=question_a, value="hello world")
    doc_b.answers.create(question=question_b, value="seeya world")

    doc_c.answers.create(question=question_a, value="goodbye planet")
    doc_c.answers.create(question=question_b, value="seeya world")

    query = """
        query ($search: [SearchAnswersFilterType!]) {
          allDocuments(filter: [{searchAnswers: $search}]) {
            edges {
              node {
                id
              }
            }
          }
        }
    """

    # Here, we send two searches, which we expect to be joined by AND.
    result = schema_executor(
        query,
        variable_values={
            "search": [
                # "hello" is in doc_a and doc_b
                {"questions": [question_a.slug], "value": "hello"},
                # "world" is in doc_b and doc_c
                {"questions": [question_b.slug], "value": "world"},
            ]
        },
    )

    assert not result.errors
    edges = result.data["allDocuments"]["edges"]

    # Result - we expect only doc_b in the result
    assert len(edges) == 1
    assert extract_global_id(edges[0]["node"]["id"]) == str(doc_b.id)


def test_search_invalid_question_type(schema_executor, db, question_factory):

    question = question_factory(type=models.Question.TYPE_FORM)

    result = schema_executor(
        """
            query ($search: [SearchAnswersFilterType!]) {
              allDocuments(filter: [{searchAnswers: $search}]) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        """,
        variable_values={"search": [{"questions": [question.slug], "value": "blah"}]},
    )

    expected_error_msg = "Questions of type form cannot be used in searchAnswers"

    assert any(expected_error_msg in str(err) for err in result.errors)


def test_search_invalid_form_slug(schema_executor, db, document_factory):
    document_factory(form__slug="foo")
    result = schema_executor(
        """
            query ($search: [SearchAnswersFilterType!]) {
              allDocuments(filter: [{searchAnswers: $search}]) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        """,
        variable_values={"search": [{"forms": ["bar"], "value": "blah"}]},
    )

    expected_error_msg = "Following forms could not be found: bar"

    assert any(expected_error_msg in str(err) for err in result.errors)


def test_search_no_parameter(schema_executor, db):
    result = schema_executor(
        """
            query ($search: [SearchAnswersFilterType!]) {
              allDocuments(filter: [{searchAnswers: $search}]) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        """,
        variable_values={"search": [{"value": "blah"}]},
    )

    expected_error_msg = '"forms" and/or "questions" parameter must be set'

    assert any(expected_error_msg in str(err) for err in result.errors)


def test_search_question_not_in_form(schema_executor, db, document):
    result = schema_executor(
        """
            query ($search: [SearchAnswersFilterType!]) {
              allDocuments(filter: [{searchAnswers: $search}]) {
                edges {
                  node {
                    id
                  }
                }
              }
            }
        """,
        variable_values={
            "search": [
                {
                    "forms": [document.form.slug],
                    "value": "blah",
                }
            ]
        },
    )

    assert not result.errors
    edges = result.data["allDocuments"]["edges"]
    assert len(edges) == 0
