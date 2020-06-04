import pytest

from ...caluma_core.relay import extract_global_id
from ...caluma_form.filters import AnswerHierarchyMode, AnswerLookupMode
from .. import models

TEST_VALUES = {
    "multiple_choice": {"matching": ["a", "b"], "nomatch": ["x"]},
    "integer": {"matching": 10, "nomatch": 99},
    "text": {"matching": "foo", "nomatch": "bar"},
    "textarea": {"matching": "foo", "nomatch": "bar"},
    "float": {"matching": 11.5, "nomatch": 99.5},
    "datetime": {
        "matching": "2018-05-09T14:54:51.728786",
        "nomatch": "2019-05-09T14:54:51.728786",
    },
    "date": {"matching": "2018-05-09", "nomatch": "2019-05-09"},
    "choice": {"matching": "a", "nomatch": "x"},
}


@pytest.mark.parametrize(
    "search_lookup", [None, *AnswerLookupMode._meta.enum.__members__]
)
@pytest.mark.parametrize("form_value", ["matching", "nomatch"])
@pytest.mark.parametrize(
    "search_slug,search_value",
    [(qtype, vals["matching"]) for qtype, vals in TEST_VALUES.items()],
)
def test_query_all_questions(
    schema_executor,
    db,
    snapshot,
    question,
    form_factory,
    form_question_factory,
    question_factory,
    document_factory,
    answer_factory,
    form_value,
    search_slug,
    search_value,
    search_lookup,
):
    # build up our form first
    top_form = form_factory()
    top_question = form_question_factory.create(
        form=top_form,
        question__slug="top_question",
        question__type=models.Question.TYPE_TEXT,
    ).question
    subform_question = form_question_factory.create(
        form=top_form,
        question__slug="subform-question",
        question__type=models.Question.TYPE_FORM,
        question__sub_form__slug="subform",
    ).question

    subform_document = document_factory(form=subform_question.sub_form)

    # "randomly" set the hierarchy lookup mode. Not parametrized, as it would
    # explode the test run time three-fold
    possible_hierarchy_lookups = [None, *AnswerHierarchyMode._meta.enum.__members__]
    hierarchy_lookup = possible_hierarchy_lookups[
        len(search_slug) % len(possible_hierarchy_lookups)
    ]

    sub_questions = {
        qtype.lower(): form_question_factory(
            question__slug=qtype.lower(),
            question__type=qtype,
            form=subform_question.sub_form,
        ).question
        for qtype in models.Question.TYPE_CHOICES
        if qtype
        not in (
            # some question types are not searchable
            models.Question.TYPE_FILE,
            models.Question.TYPE_TABLE,
            models.Question.TYPE_FORM,
            models.Question.TYPE_DYNAMIC_CHOICE,
            models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE,
            models.Question.TYPE_STATIC,
        )
    }

    # Now, make a document for it

    result = schema_executor(
        """
            mutation foo ($form_id: ID!){
                saveDocument(input: {form: $form_id}) {
                    document {
                      id
                    }
                }
            }
        """,
        variable_values={"form_id": top_form.pk},
    )

    document_id = extract_global_id(result.data["saveDocument"]["document"]["id"])
    document = models.Document.objects.get(pk=document_id)
    # just some other answer
    answer_factory(question=top_question, document=document, value="foo")

    for qtype, question in sub_questions.items():
        if qtype == models.Question.TYPE_DATE:
            answer_factory(
                question=question,
                document=subform_document,
                date=TEST_VALUES[qtype][form_value],
            )
        else:
            answer_factory(
                question=question,
                document=subform_document,
                value=TEST_VALUES[qtype][form_value],
            )

    query = """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                form {
                  slug
                }
              }
            }
          }
        }
    """

    variables = {"hasAnswer": [{"question": search_slug, "value": search_value}]}
    if search_lookup is not None:
        variables["hasAnswer"][0]["lookup"] = search_lookup
    if hierarchy_lookup is not None:
        variables["hasAnswer"][0]["hierarchy"] = hierarchy_lookup

    result = schema_executor(query, variable_values=variables)
    # note: result.errors may contain stuff that pytest-snapshottest cannot
    # serialize properly, thus we stringify it
    snapshot.assert_match(
        {
            "request": {"query": query, "variables": variables},
            "response": {"errors": str(result.errors), "data": result.data},
        }
    )


@pytest.mark.parametrize(
    "question__type,value,search,expect_find",
    [
        (models.Question.TYPE_MULTIPLE_CHOICE, ["a", "b"], ["a"], True),
        (models.Question.TYPE_MULTIPLE_CHOICE, ["a", "b"], ["c"], False),
        (models.Question.TYPE_CHOICE, "foo", ["foo", "bar"], True),
        (models.Question.TYPE_CHOICE, "foo", ["bar", "baz"], False),
        (models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, ["a", "b"], ["a"], True),
        (models.Question.TYPE_DYNAMIC_MULTIPLE_CHOICE, ["a", "b"], ["c"], False),
        (models.Question.TYPE_DYNAMIC_CHOICE, "foo", ["foo", "bar"], True),
        (models.Question.TYPE_DYNAMIC_CHOICE, "foo", ["bar", "baz"], False),
    ],
)
def test_has_answer_intersect(
    schema_executor,
    db,
    question,
    document_factory,
    answer_factory,
    value,
    search,
    expect_find,
):
    doc = document_factory()
    answer_factory(document=doc, question=question, value=value)

    query = """
        query asdf ($hasAnswer: [HasAnswerFilterType]!) {
          allDocuments(hasAnswer: $hasAnswer) {
            edges {
              node {
                id
              }
            }
          }
        }
    """
    variables = {
        "hasAnswer": [
            {"question": question.slug, "value": search, "lookup": "INTERSECTS"}
        ]
    }

    result = schema_executor(query, variable_values=variables)
    assert not result.errors

    expect_count = 1 if expect_find else 0

    assert len(result.data["allDocuments"]["edges"]) == expect_count


@pytest.mark.parametrize("question__is_hidden,expected", [("false", 1), ("true", 0)])
def test_visible_in_context(
    schema_executor, db, document, form, question, form_question, answer, expected
):
    query = """
        query asdf ($visible: Boolean!) {
          allDocuments {
            edges {
              node {
                answers(visibleInContext: $visible) {
                  edges {
                    node {
                      id
                    }
                  }
                }
              }
            }
          }
        }
    """
    variables = {"visible": True}

    result = schema_executor(query, variable_values=variables)
    assert not result.errors
    assert (
        len(result.data["allDocuments"]["edges"][0]["node"]["answers"]["edges"])
        == expected
    )
