import pytest
from graphql_relay import to_global_id

from ...caluma_core.tests import extract_serializer_input_fields
from .. import models, serializers


def test_save_option(db, option, snapshot, schema_executor):
    query = """
        mutation SaveOption($input: SaveOptionInput!) {
          saveOption(input: $input) {
            option {
              slug
              label
            }
          }
        }
    """

    inp = {
        "input": extract_serializer_input_fields(
            serializers.SaveOptionSerializer, option
        )
    }

    result = schema_executor(query, variable_values=inp)
    assert not result.errors
    snapshot.assert_match(result.data)


@pytest.mark.parametrize("option__meta", [{"meta": "set"}])
def test_copy_option(db, option, schema_executor):
    query = """
        mutation CopyOption($input: CopyOptionInput!) {
          copyOption(input: $input) {
            option {
              slug
            }
          }
        }
    """

    inp = {"input": {"source": option.pk, "slug": "new-option", "label": "Test Option"}}
    result = schema_executor(query, variable_values=inp)

    assert not result.errors

    option_slug = result.data["copyOption"]["option"]["slug"]
    assert option_slug == "new-option"
    new_option = models.Option.objects.get(pk=option_slug)
    assert new_option.label == "Test Option"
    assert new_option.meta == option.meta
    assert new_option.source == option


@pytest.fixture(params=[models.Question.TYPE_CHOICE, True])
def option_jexl_setup(
    document,
    question_option_factory,
    question_factory,
    answer_document_factory,
    form_question_factory,
    request,
):
    def setup():
        question_type, is_hidden = request.param
        text_question = question_factory(type=models.Question.TYPE_TEXT)
        is_hidden_jexl = "false"
        if is_hidden:
            is_hidden_jexl = f"'{text_question.slug}'|answer == 'foo'"
        question_option = question_option_factory(
            option__is_hidden=is_hidden_jexl,
            option__slug="bar",
            question__type=question_type,
        )
        question_option_selected = question_option_factory(
            question=question_option.question
        )
        answer_document_factory(
            document=document,
            answer__document=document,
            answer__question=text_question,
            answer__value="foo",
        )
        answer_document_factory(
            document=document,
            answer__document=document,
            answer__question=question_option.question,
            answer__value=question_option_selected.option.pk,
        )
        form_question_factory(form=document.form, question=question_option.question)
        form_question_factory(form=document.form, question=text_question)
        return document, is_hidden, question_option

    return setup


@pytest.mark.parametrize(
    "option_jexl_setup,option_for_multiple_questions",
    [
        (
            [models.Question.TYPE_CHOICE, True],
            False,
        ),
        (
            [models.Question.TYPE_CHOICE, False],
            False,
        ),
        (
            [models.Question.TYPE_MULTIPLE_CHOICE, True],
            False,
        ),
        (
            [models.Question.TYPE_MULTIPLE_CHOICE, False],
            False,
        ),
        (
            [models.Question.TYPE_CHOICE, True],
            True,
        ),
    ],
    indirect=["option_jexl_setup"],
)
def test_option_is_hidden(
    db,
    option_jexl_setup,
    option_for_multiple_questions,
    question_option_factory,
    question_factory,
    schema_executor,
):
    document, is_hidden, question_option = option_jexl_setup()
    if option_for_multiple_questions:
        question_option_factory(
            option=question_option.option, question=question_factory()
        )

    query = """
        query Document($id: ID!, $question_id: ID!) {
          allDocuments(filter: [{id: $id}]) {
            edges {
              node {
                answers(filter: [{question: $question_id}]) {
                  edges {
                    node {
                      ... on StringAnswer {
                        question {
                          ... on ChoiceQuestion {
                            options(filter: [{visibleInDocument: $id}]) {
                              edges {
                                node {
                                  slug
                                }
                              }
                            }
                          }
                        }
                      }
                      ... on ListAnswer {
                        question {
                          ... on MultipleChoiceQuestion {
                            options(filter: [{visibleInDocument: $id}]) {
                              edges {
                                node {
                                  slug
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """

    variables = {
        "id": to_global_id("Document", document),
        "question_id": to_global_id("Question", question_option.question.pk),
    }

    result = schema_executor(query, variable_values=variables)
    assert bool(result.errors) is option_for_multiple_questions
    if option_for_multiple_questions:
        assert len(result.errors) == 1
        assert result.errors[0].message == (
            "[ErrorDetail(string='The `visibleInDocument`-filter can only be used if "
            "the filtered Options all belong to one unique question', code='invalid')]"
        )
        return

    options = result.data["allDocuments"]["edges"][0]["node"]["answers"]["edges"][0][
        "node"
    ]["question"]["options"]["edges"]
    expected = [{"node": {"slug": "bar"}}, {"node": {"slug": "thing-piece"}}]
    if is_hidden:
        expected = [{"node": {"slug": "thing-piece"}}]
    assert options == expected


@pytest.mark.parametrize(
    "option_jexl_setup",
    [
        [models.Question.TYPE_CHOICE, True],
        [models.Question.TYPE_CHOICE, False],
    ],
    indirect=["option_jexl_setup"],
)
def test_option_is_hidden_save(
    db,
    option_jexl_setup,
    schema_executor,
):
    document, is_hidden, choice_question_option = option_jexl_setup()

    query = """
        mutation saveDocumentStringAnswer($input: SaveDocumentStringAnswerInput!) {
          saveDocumentStringAnswer(input: $input) {
            answer {
              __typename
            }
          }
        }
    """

    variables = {
        "input": {
            "document": to_global_id("Document", document.pk),
            "question": to_global_id(
                "ChoiceQuestion", choice_question_option.question.pk
            ),
            "value": choice_question_option.option.pk,
        }
    }

    result = schema_executor(query, variable_values=variables)
    assert bool(result.errors) is is_hidden


@pytest.mark.parametrize(
    "option_jexl_setup",
    [
        [models.Question.TYPE_CHOICE, True],
        [models.Question.TYPE_CHOICE, False],
    ],
    indirect=["option_jexl_setup"],
)
def test_validate_form_with_jexl_option(db, option_jexl_setup, schema_executor):
    """Ensure full document validation with JEXL options works as intended.

    This triggers some internal validator flows from the document validator
    to the answer validator that we need to ensure works correctly, as it
    depends on proper handling of the form structure data, passing it down
    from document to answer validator.
    """
    document, is_hidden, choice_question_option = option_jexl_setup()

    query = """
        query($id: ID!) {
          documentValidity(id: $id) {
            edges {
              node {
                id
                isValid
                errors {
                  slug
                  errorMsg
                }
              }
            }
          }
        }
    """

    result = schema_executor(query, variable_values={"id": str(document.id)})

    assert not result.errors
